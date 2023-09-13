from pathlib import Path
from deep_sort_realtime.deepsort_tracker import DeepSort
from drawer import Drawer
from misc import save_frame, save_chips
import cv2
import threading
import copy

import logging
from base_component import BaseComponent

logging.basicConfig(level=logging.INFO)


class Component(BaseComponent):

    def __init__(self, config):
        super().__init__(config)

        self.seconds = config.seconds
        self.infer_fps = config.infer_fps
        self.classes_list = ['person']
        self.output_dir = Path(config.output_dir)
        self.crop_chips = config.save_chips
        self.record_tracks = config.record_tracks

        self.drawer = Drawer(color=(255, 0, 0))
        self.tracker = DeepSort(max_age=30, nn_budget=10, embedder='torchreid')

        logging.info(f'Making output folder at: {self.output_dir}')
        if self.record_tracks:
            self.frames_save_dir = self.output_dir / f'0_frames'
            self.frames_save_dir.mkdir(parents=True, exist_ok=True)

            # self.out_track_fp = self.output_dir / f'0_inference.avi'
            # self.out_track = cv2.VideoWriter(str(self.out_track_fp), cv2.VideoWriter_fourcc(*'MJPG'), self.infer_fps, (1080, 1920))

        if self.crop_chips:
            self.chips_save_dir = self.output_dir / f'0_crops'
            self.chips_save_dir.mkdir(parents=True, exist_ok=True)

        self.frame_id = 0


    def process(self, frame, raw_detections):
        logging.info(f'processing frame id: {self.frame_id}')

        all_detections = [tuple((d[:4], d[4], self.classes_list[int(d[5])])) for d in raw_detections.tolist()]  # TODO change
        logging.info(f'all detections: {all_detections}')
        all_tracks = self.tracker.update_tracks(frame=frame, raw_detections=all_detections)
        logging.info(f'all tracks: {[vars(track) for track in all_tracks]}')

        if len(all_tracks) != 0:
            if self.record_tracks:
                threading.Thread(target=save_frame, args=(copy.deepcopy(frame), self.frame_id, all_tracks, self.frames_save_dir, self.drawer), daemon=True).start()

            if self.crop_chips:
                threading.Thread(target=save_chips, args=(copy.deepcopy(frame), self.frame_id, all_tracks, self.chips_save_dir, '0'),
                                 daemon=True).start()

        self.frame_id += 1
