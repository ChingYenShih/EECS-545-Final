import torch
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
import cv2

def save_attention_map(model, testing_rgb, testing_lidar, testing_mask):
    x_global, x_local, global_attn, local_attn = model(testing_rgb, testing_lidar, testing_mask)
    predict_depth = get_predicted_depth(x_global, x_local, global_attn, local_attn)
    
    b, _, h, w = x_global.size()

    pred_attn = torch.zeros((b, 2, h, w)).to(x_global.device)#torch.zeros_like(color_path_dense) # b x 2 x 128 x 256
    pred_attn[:, 0, :, :] = global_attn
    pred_attn[:, 1, :, :] = local_attn
    pred_attn = F.softmax(pred_attn, dim=1) # b x 2 x 128 x 256

    global_attn, local_attn = pred_attn[:, 0, :, :], pred_attn[:, 1, :, :]
    print(global_attn.size(), torch.max(global_attn), torch.min(global_attn))
    print(x_global.size(), torch.max(x_global), torch.min(x_global))

    cv2.imwrite("global.png", x_global.squeeze(0).detach().numpy().transpose(1,2,0))
    cv2.imwrite("local.png", x_local.squeeze(0).detach().numpy().transpose(1,2,0))
    cv2.imwrite("predict_depth.png", predict_depth.squeeze(0).detach().numpy().transpose(1,2,0))
    cv2.imwrite("global_attn.png", global_attn.detach().numpy().transpose(1,2,0)*255)
    cv2.imwrite("local_attn.png", local_attn.detach().numpy().transpose(1,2,0)*255)
    exit()
def get_predicted_depth(color_path_dense, normal_path_dense, color_attn, normal_attn):
    """Use raw model output to generate dense of color pathway, normal path way, and integrated result
    Returns: predicted_dense, pred_color_path_dense, pred_normal_path_dense
    """
    # get predicted dense depth from 2 pathways
    b, _, h, w = color_path_dense.size()
    pred_color_path_dense = color_path_dense[:, 0, :, :] # b x 128 x 256
    pred_normal_path_dense = normal_path_dense[:, 0, :, :]

    # get attention map of 2 pathways
    color_attn = torch.squeeze(color_attn) # b x 128 x 256
    normal_attn = torch.squeeze(normal_attn) # b x 128 x 256

    # softmax 2 attention map
    pred_attn = torch.zeros((b, 2, h, w)).to(color_path_dense.device)#torch.zeros_like(color_path_dense) # b x 2 x 128 x 256
    pred_attn[:, 0, :, :] = color_attn
    pred_attn[:, 1, :, :] = normal_attn
    pred_attn = F.softmax(pred_attn, dim=1) # b x 2 x 128 x 256

    color_attn, normal_attn = pred_attn[:, 0, :, :], pred_attn[:, 1, :, :]

    # get predicted dense from weighted sum of 2 path way
    predicted_dense = pred_color_path_dense * color_attn + pred_normal_path_dense * normal_attn # b x 128 x 256

    predicted_dense = predicted_dense.unsqueeze(1)
    pred_color_path_dense = pred_color_path_dense.unsqueeze(1) 
    pred_normal_path_dense = pred_normal_path_dense.unsqueeze(1)

    return predicted_dense

def get_depth_and_normal(model, rgb, lidar, mask):
    """Given model and input of model, get dense depth and surface normal

    Returns:
    predicted_dense: b x c x h x w
    pred_surface_normal: b x c x h x w
    """
    model.eval()
    with torch.no_grad():
        x_global, x_local, global_attn, local_attn = model(rgb, lidar, mask)
    predicted_dense = get_predicted_depth(x_global, x_local, global_attn, local_attn)

    return predicted_dense




def normal_to_0_1(img):
    """Normalize image to [0, 1], used for tensorboard visualization."""
    return (img - torch.min(img)) / (torch.max(img) - torch.min(img))


def normal_loss(pred_normal, gt_normal, gt_normal_mask):
    """Calculate loss of surface normal (in the stage N)

    Params:
    pred: b x 3 x 128 x 256
    normal_gt: b x 3 x 128 x 256
    normal_mask: b x 3 x 128 x 256
    """

    valid_mask = (gt_normal_mask > 0.0).detach()

    #pred_n = pred.permute(0,2,3,1)
    pred_normal = pred_normal[valid_mask]
    gt_normal = gt_normal[valid_mask]

    pred_normal = pred_normal.contiguous().view(-1,3)
    pred_normal = F.normalize(pred_normal)
    gt_normal = gt_normal.contiguous().view(-1, 3)

    loss_function = nn.CosineEmbeddingLoss()
    loss = loss_function(pred_normal, gt_normal, torch.Tensor(pred_normal.size(0)).to(pred_normal.device).fill_(1.0))
    return loss



def get_depth_loss(dense, gt):
    """
    dense: b x 1 x 128 x 256
    c_dense: b x 1 x 128 x 256
    n_dense: b x 1 x 128 x 256
    gt: b x 1 x 128 x 256
    params: b x 3 x 128 x 256
    normals: b x 128 x 256 x 3
    """
    valid_mask = (gt > 0.0).detach() # b x 1 x 128 x 256
    gt = gt[valid_mask]
    dense = dense[valid_mask]

    criterion = nn.MSELoss()
    loss = torch.sqrt(criterion(dense, gt))

    
    return loss




def get_loss(predicted_dense, gt_depth):
    return get_depth_loss(predicted_dense, gt_depth)


