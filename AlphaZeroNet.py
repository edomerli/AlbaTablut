from pytorch_lightning.utilities.types import OptimizerLRScheduler
import torch
from torch import nn
from typing import NamedTuple, Tuple
import pytorch_lightning as pl


class NetworkOutputs(NamedTuple):
    pi_prob: torch.Tensor
    value: torch.Tensor

def initialize_weights(layer: nn.Module) -> None:
    """Initialize weights for Conv2d and Linear layers using Kaming He initializer"""
    if isinstance(layer, (nn.Conv2d, nn.Linear)):
        nn.init.kaiming_uniform_(layer.weight, nonlinearity='relu')

        if layer.bias is not None:
            nn.init.zeros_(layer.bias)


class ResNetBlock(nn.Module):
    """Basic redisual block."""

    def __init__(
        self,
        num_filters: int,
    ) -> None:
        super().__init__()

        self.conv_block1 = nn.Sequential(
            nn.Conv2d(
                in_channels=num_filters,
                out_channels=num_filters,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=num_filters),
            nn.ReLU(),
        )

        self.conv_block2 = nn.Sequential(
            nn.Conv2d(
                in_channels=num_filters,
                out_channels=num_filters,
                kernel_size=3,
                stride=1,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=num_filters),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.conv_block1(x)
        out = self.conv_block2(out)
        out += residual
        out = nn.functional.relu(out)
        return out
    

class AlphaZeroNet(pl.LightningModule):
    """Policy network for AlphaZero agent."""

    def __init__(
        self,
        input_shape: Tuple,
        num_actions: int,
        num_res_block: int = 19,
        num_filters: int = 256,
        num_fc_units: int = 256,
        # gomoku: bool = False,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()    # save all hyperparameters to self.hparams for checkpointing 

        c, h, w = input_shape   # channel first!

        num_padding = 1

        # TODO: remove eventually
        # conv_out_hw = calc_conv2d_output((h, w), 3, 1, num_padding)
        # conv_out = conv_out_hw[0] * conv_out_hw[1]
        conv_out = h * w

        # First convolutional block
        self.conv_block = nn.Sequential(
            nn.Conv2d(
                in_channels=c,
                out_channels=num_filters,
                kernel_size=3,
                stride=1,
                padding=num_padding,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=num_filters),
            nn.ReLU(),
        )

        # Residual blocks
        res_blocks = []
        for _ in range(num_res_block):
            res_blocks.append(ResNetBlock(num_filters))
        self.res_blocks = nn.Sequential(*res_blocks)

        self.policy_head = nn.Sequential(
            nn.Conv2d(
                in_channels=num_filters,
                out_channels=2,
                kernel_size=1,
                stride=1,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * conv_out, num_actions),
            nn.Softmax(dim=1)
        )

        self.value_head = nn.Sequential(
            nn.Conv2d(
                in_channels=num_filters,
                out_channels=1,
                kernel_size=1,
                stride=1,
                bias=False,
            ),
            nn.BatchNorm2d(num_features=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(1 * conv_out, num_fc_units),
            nn.ReLU(),
            nn.Linear(num_fc_units, 1),
            nn.Tanh(),
        )

        self.apply(initialize_weights)

        self.optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)


    def forward(self, x: torch.Tensor) -> NetworkOutputs:
        """Given raw state x, predict the raw logits probability distribution for all actions,
        and the evaluated value, all from current player's perspective."""

        conv_block_out = self.conv_block(x)
        features = self.res_blocks(conv_block_out)

        # Predict raw logits distributions wrt policy
        pi_logits = self.policy_head(features)

        # Predict evaluated value from current player's perspective.
        value = self.value_head(features)

        return pi_logits, value
    
    def training_step(self, train_batch, batch_idx):
        
        board, target_pi, target_v = train_batch

        pred_pi_logits, pred_v = self(board)

        loss = self._losses(pred_pi_logits, torch.squeeze(pred_v), target_pi, target_v)
        self.log('train_loss', loss)

        return loss

    def _losses(self, pred_pi_logits, pred_v, target_pi, target_v):
        policy_loss = nn.functional.cross_entropy(pred_pi_logits, target_pi)
        value_loss = nn.functional.mse_loss(pred_v, target_v)
        return policy_loss + value_loss
    
    def configure_optimizers(self) -> OptimizerLRScheduler:
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        return optimizer