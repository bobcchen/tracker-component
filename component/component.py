from pathlib import Path
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np

import logging
from base_component import BaseComponent

logging.basicConfig(level=logging.INFO)


class Component(BaseComponent):

    def __init__(self, config):
        super().__init__(config)

        self.classes_list = ['person', 'boat', 'traffic light', 'surfboard']
        self.tracker = DeepSort(max_age=30, nn_budget=10, embedder='torchreid')

        self.frame_id = 0


    def process(self, frame, raw_detections):
        self.frame_id += 1
        logging.info(f'processing frame id: {self.frame_id}')

        all_detections = [tuple((d[:4], d[4], self.classes_list[int(d[5])])) for d in raw_detections.tolist()]  # TODO change
        # logging.info(f'all detections: {all_detections}')
        all_tracks = self.tracker.update_tracks(frame=frame, raw_detections=all_detections)
        # logging.info(f'all tracks: {[vars(track) for track in all_tracks]}')

        # return tracks for drawing purposes
        result = []
        for track in all_tracks:
            if not track.is_confirmed() or track.time_since_update > 0:
                continue
            track_bb = [int(x) for x in track.to_ltrb(orig=True)]
            track_bb.append(track.track_id)
            result.append(track_bb)
        result = np.array(result, dtype='i4')
        logging.info(f'confirmed tracks bb: {result}')
        return result
