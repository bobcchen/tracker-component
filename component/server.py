from component import Component

import argparse
import signal

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', default='A')
    parser.add_argument('--next_service', default=None)
    parser.add_argument('--init_retries', default=5, type=int)
    parser.add_argument('--pipeline_id', default=0, type=str)

    parser.add_argument('--infer_fps', help='FPS for inference (use higher fps for deepsort to work better)', type=int,
                        default=4)
    parser.add_argument('--output_dir', help='Path of output directory', default='output')
    parser.add_argument('--save_chips', help='Whether to save cropped chips', action='store_true')
    parser.add_argument('--seconds', help='Number of seconds between each chip save', type=int, default=1)
    parser.add_argument('--record_tracks', help='Whether to save inference video', action='store_true')
    args = parser.parse_args()

    server = Component(args)

    run = True

    def handler(signum, frame):
        global run
        run = False


    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    while run:
        server.run()

    server.shutdown()
