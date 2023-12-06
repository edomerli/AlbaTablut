import socket
import struct
import sys
import json

from Board import Board
from AlphaZeroNet import AlphaZeroNet
from AI import AI
from utils import *
from pathlib import Path

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def move_to_json(move, color):
    from_pos = move[0]
    to_pos = move[1]
    turn = color.upper()

    from_literal = chr(from_pos[0] + 97) + str(from_pos[1] + 1)
    to_literal = chr(to_pos[0] + 97) + str(to_pos[1] + 1)

    return {
        'from': from_literal,
        'to': to_literal,
        'turn': turn
    }

if __name__ == "__main__":

    color = sys.argv[1].lower() if len(sys.argv) >= 2 else 'white'
    timeout = int(sys.argv[2]) if len(sys.argv) >= 3 else 60
    server_ip = sys.argv[3] if len(sys.argv) >= 4 else 'localhost'

    # define AI and load models
    ai = AI(AI_BUDGET, WHITE_PLAYER if color == 'white' else BLACK_PLAYER)
    WHITE_AI_PATH = Path('./ckpts/white_model.ckpt')
    BLACK_AI_PATH = Path('./ckpts/black_model.ckpt')

    white_alphazero = None
    black_alphazero = None
    if WHITE_AI_PATH.is_file():
        white_alphazero = AlphaZeroNet.load_from_checkpoint(WHITE_AI_PATH)
    if BLACK_AI_PATH.is_file():
        black_alphazero = AlphaZeroNet.load_from_checkpoint(BLACK_AI_PATH)

    if white_alphazero is not None and black_alphazero is not None:
        ai.alphazero = white_alphazero if color == 'white' else black_alphazero
        ai.opponent = black_alphazero if color == 'white' else white_alphazero
    else:
        raise Exception("Models not found")
    

    # define server port depending on color
    if color == 'white':
        server_address = (server_ip, 5800)
    elif color == 'black':
        server_address = (server_ip, 5801)
    else:
        raise Exception("Se giochi o sei bianco oppure sei nero")
    
    # connect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        player_name="AlbaTablut"
        sock.send(struct.pack('>i', len(player_name)))
        sock.send(player_name.encode())

        # read extra initial state from server if you are black
        if color == 'black':
            len_bytes = struct.unpack('>i', recvall(sock, 4))[0]
            current_state_server_bytes = sock.recv(len_bytes).decode('utf-8')

        while True:
            len_bytes = struct.unpack('>i', recvall(sock, 4))[0]
            current_state_server_bytes = sock.recv(len_bytes).decode('utf-8')

            json_current_state_server = json.loads(current_state_server_bytes)
                    
            board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1], json_current_state_server['board'], turn=json_current_state_server['turn'])

            # MCTS search
            move, _, _ = ai.MCTS(board, timeout=timeout)

            # Convert from coordinates move to literals move
            move_for_server = json.dumps(move_to_json(move, color))

            sock.send(struct.pack('>i', len(move_for_server)))
            sock.send(move_for_server.encode())

            # read response from server with the modified board by this move
            len_bytes = struct.unpack('>i', recvall(sock, 4))[0]
            current_state_server_bytes = sock.recv(len_bytes).decode('utf-8')
