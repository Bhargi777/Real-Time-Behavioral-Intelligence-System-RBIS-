import numpy as np
from scipy.optimize import linear_sum_assignment

def iou_batch(bboxes1, bboxes2):
    """
    Compute Intersection over Union (IoU) between two sets of bounding boxes.
    bboxes1: (N, 4)  [x1, y1, x2, y2]
    bboxes2: (M, 4)  [x1, y1, x2, y2]
    """
    # [x, y, w, h] to [x1, y1, x2, y2]
    def to_ltrb(box):
        return [box[0], box[1], box[0]+box[2], box[1]+box[3]]
        
    bboxes1_ltrb = np.array([to_ltrb(box) for box in bboxes1])
    bboxes2_ltrb = np.array([to_ltrb(box) for box in bboxes2])
    
    # Broadcast subtraction
    xx1 = np.maximum(bboxes1_ltrb[:, np.newaxis, 0], bboxes2_ltrb[np.newaxis, :, 0])
    yy1 = np.maximum(bboxes1_ltrb[:, np.newaxis, 1], bboxes2_ltrb[np.newaxis, :, 1])
    xx2 = np.minimum(bboxes1_ltrb[:, np.newaxis, 2], bboxes2_ltrb[np.newaxis, :, 2])
    yy2 = np.minimum(bboxes1_ltrb[:, np.newaxis, 3], bboxes2_ltrb[np.newaxis, :, 3])
    
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    
    area1 = (bboxes1_ltrb[:, 2] - bboxes1_ltrb[:, 0]) * (bboxes1_ltrb[:, 3] - bboxes1_ltrb[:, 1])
    area2 = (bboxes2_ltrb[:, 2] - bboxes2_ltrb[:, 0]) * (bboxes2_ltrb[:, 3] - bboxes2_ltrb[:, 1])
    
    iou = wh / (area1[:, np.newaxis] + area2[np.newaxis, :] - wh)
    return iou

def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """
    Assigns detections to tracked object (both represent (x, y, w, h)).
    Returns 3 lists: matches, unmatched_detections, unmatched_trackers
    """
    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0, 5), dtype=int)
        
    iou_matrix = iou_batch(detections, trackers)
    
    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = np.stack(linear_sum_assignment(-iou_matrix), axis=1)
    else:
        matched_indices = np.empty((0, 2))
        
    unmatched_detections = []
    for d, det in enumerate(detections):
        if d not in matched_indices[:, 0]:
            unmatched_detections.append(d)
            
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if t not in matched_indices[:, 1]:
            unmatched_trackers.append(t)
            
    # filter out matches with low IoU
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1, 2))
            
    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)
        
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)
