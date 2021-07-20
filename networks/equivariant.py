import torch
import torch.nn.functional as F

from e2cnn import gspaces
from e2cnn import nn

# class EquivariantCNNFac(torch.nn.Module):
#     def __init__(self, initialize=True, n_p=2, n_theta=1):
#         super().__init__()
#         self.r2_act = gspaces.Rot2dOnR2(4)
#         self.conv = torch.nn.Sequential(
#             # 128x128
#             nn.R2Conv(nn.FieldType(self.r2_act, 2*[self.r2_act.trivial_repr]),
#                       nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]),
#                       kernel_size=3, padding=1, initialize=initialize),
#             nn.ReLU(nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]), inplace=True),
#             nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]), 2),
#             # 64x64
#             nn.R2Conv(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
#                       kernel_size=3, padding=1, initialize=initialize),
#             nn.ReLU(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), inplace=True),
#             nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), 2),
#             # 32x32
#             nn.R2Conv(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
#                       kernel_size=3, padding=1, initialize=initialize),
#             nn.ReLU(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), inplace=True),
#             nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), 2),
#             # 16x16
#             nn.R2Conv(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
#                       kernel_size=3, padding=1, initialize=initialize),
#             nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
#             nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), 2),
#             # 8x8
#             nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
#                       kernel_size=3, padding=1, initialize=initialize),
#             nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),
#         )
#
#         self.dxy_layer = torch.nn.Sequential(
#             nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
#                       kernel_size=8, padding=0),
#             nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
#             nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
#                       nn.FieldType(self.r2_act, 2 * [self.r2_act.regular_repr]),
#                       kernel_size=1, padding=0),
#         )
#
#         self.group_pool = nn.GroupPooling(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]))
#         self.fc1 = torch.nn.Sequential(
#             torch.nn.Flatten(),
#             torch.nn.Linear(256*8*8, 1024),
#             torch.nn.ReLU(inplace=True),
#         )
#
#         self.p_layer = torch.nn.Sequential(
#             torch.nn.Linear(1024, n_p)
#         )
#
#         self.dz_layer = torch.nn.Sequential(
#             torch.nn.Linear(1024, 3)
#         )
#
#         self.dtheta_layer = torch.nn.Sequential(
#             torch.nn.Linear(1024, n_theta)
#         )
#
#         self.dxy0_layer = torch.nn.Sequential(
#             torch.nn.Linear(1024, 1)
#         )
#
#     def forward(self, x):
#         batch_size = x.shape[0]
#         x = nn.GeometricTensor(x, nn.FieldType(self.r2_act, 2*[self.r2_act.trivial_repr]))
#         h = self.conv(x)
#         dxy = self.dxy_layer(h).tensor.reshape(batch_size, 2, 4)
#         inv_h = self.fc1(self.group_pool(h).tensor)
#         dxy0 = self.dxy0_layer(inv_h)
#         dxy = torch.stack((dxy0[:, 0],
#                            dxy[:, 0, 0], dxy[:, 1, 0], dxy[:, 0, 1],
#                            dxy[:, 1, 3], dxy[:, 1, 1],
#                            dxy[:, 0, 3], dxy[:, 1, 2], dxy[:, 0, 2]),
#                           dim=1)
#         p = self.p_layer(inv_h)
#         dz = self.dz_layer(inv_h)
#         dtheta = self.dtheta_layer(inv_h)
#         return p, dxy, dz, dtheta

class EquivariantCNNFac(torch.nn.Module):
    def __init__(self, initialize=True, n_p=2, n_theta=1):
        super().__init__()
        self.n_inv = 1 + 3 + n_theta + n_p
        self.n_theta = n_theta
        self.n_p = n_p

        self.r2_act = gspaces.Rot2dOnR2(4)
        self.conv = torch.nn.Sequential(
            # 128x128
            nn.R2Conv(nn.FieldType(self.r2_act, 2 * [self.r2_act.trivial_repr]),
                      nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]), 2),
            # 64x64
            nn.R2Conv(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), 2),
            # 32x32
            nn.R2Conv(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), 2),
            # 16x16
            nn.R2Conv(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), 2),
            # 8x8
            nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),

            # 8x8
            nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=0),
            nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), 2),
            # 3x3
            nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=0),
            nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),
            # 1x1
            nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, self.n_inv * [self.r2_act.trivial_repr] + 2 * [self.r2_act.regular_repr]),
                      kernel_size=1, padding=0),
        )

    def forward(self, x):
        batch_size = x.shape[0]
        x = nn.GeometricTensor(x, nn.FieldType(self.r2_act, 2 * [self.r2_act.trivial_repr]))
        out = self.conv(x)
        dxy0 = out[:, 0:1].tensor.reshape(batch_size, 1)
        dz = out[:, 1:4].tensor.reshape(batch_size, 3)
        dtheta = out[:, 4:4+self.n_theta].tensor.reshape(batch_size, self.n_theta)
        p = out[:, 4+self.n_theta:4+self.n_theta+self.n_p].tensor.reshape(batch_size, self.n_p)
        dxy = out[:, 4+self.n_theta+self.n_p:].tensor.reshape(batch_size, 2, 4)

        dxy = torch.stack((dxy[:, 0, 0], dxy[:, 1, 0], dxy[:, 0, 1],
                           dxy[:, 1, 3], dxy0[:, 0], dxy[:, 1, 1],
                           dxy[:, 0, 3], dxy[:, 1, 2], dxy[:, 0, 2]),
                          dim=1)
        return p, dxy, dz, dtheta

# 3x3 out
class EquivariantCNNCom(torch.nn.Module):
    def __init__(self, initialize=True, n_p=2, n_theta=1):
        super().__init__()
        self.n_inv = 3 * n_theta * n_p
        self.r2_act = gspaces.Rot2dOnR2(4)
        self.conv = torch.nn.Sequential(
            # 128x128
            nn.R2Conv(nn.FieldType(self.r2_act, 2*[self.r2_act.trivial_repr]),
                      nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 16*[self.r2_act.regular_repr]), 2),
            # 64x64
            nn.R2Conv(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), 2),
            # 32x32
            nn.R2Conv(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), 2),
            # 16x16
            nn.R2Conv(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), 2),
            # 8x8
            nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),

            nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=0),
            nn.ReLU(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]), 2),
            # 3x3
            nn.R2Conv(nn.FieldType(self.r2_act, 256 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, self.n_inv * [self.r2_act.trivial_repr]),
                      kernel_size=1, padding=0),
        )

    def forward(self, x):
        batch_size = x.shape[0]
        x = nn.GeometricTensor(x, nn.FieldType(self.r2_act, 2 * [self.r2_act.trivial_repr]))
        out = self.conv(x).tensor.reshape(batch_size, self.n_inv, 9).permute(0, 2, 1)
        return out

# 1x1 out fill
class EquivariantCNNCom2(torch.nn.Module):
    def __init__(self, initialize=True, n_p=2, n_theta=1):
        super().__init__()
        self.n_inv = 3 * n_theta * n_p
        self.r2_act = gspaces.Rot2dOnR2(8)
        self.conv = torch.nn.Sequential(
            # 128x128
            nn.R2Conv(nn.FieldType(self.r2_act, 2*[self.r2_act.trivial_repr]),
                      nn.FieldType(self.r2_act, 8*[self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 8*[self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 8*[self.r2_act.regular_repr]), 2),
            # 64x64
            nn.R2Conv(nn.FieldType(self.r2_act, 8 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]), 2),
            # 32x32
            nn.R2Conv(nn.FieldType(self.r2_act, 16 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]), 2),
            # 16x16
            nn.R2Conv(nn.FieldType(self.r2_act, 32 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]), 2),
            # 8x8
            nn.R2Conv(nn.FieldType(self.r2_act, 64 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=1, initialize=initialize),
            nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),

            # 8x8
            nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=0),
            nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
            nn.PointwiseMaxPool(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), 2),
            # 3x3
            nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      kernel_size=3, padding=0),
            nn.ReLU(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]), inplace=True),
            # 1x1
            nn.R2Conv(nn.FieldType(self.r2_act, 128 * [self.r2_act.regular_repr]),
                      nn.FieldType(self.r2_act, self.n_inv * [self.r2_act.trivial_repr] + self.n_inv * [self.r2_act.regular_repr]),
                      kernel_size=1, padding=0),
        )

    def forward(self, x):
        batch_size = x.shape[0]
        x = nn.GeometricTensor(x, nn.FieldType(self.r2_act, 2 * [self.r2_act.trivial_repr]))
        dxy = self.conv(x)
        dxy_0 = dxy[:, :self.n_inv].tensor.reshape(batch_size, self.n_inv, 1)
        dxy_1 = dxy[:, self.n_inv:].tensor.reshape(batch_size, self.n_inv, 8)
        dxy = torch.stack((dxy_1[:, :, 0], dxy_1[:, :, 1], dxy_1[:, :, 2],
                           dxy_1[:, :, 7], dxy_0[:, :, 0], dxy_1[:, :, 3],
                           dxy_1[:, :, 6], dxy_1[:, :, 5], dxy_1[:, :, 4]),
                          dim=1)

        return dxy

if __name__ == '__main__':
    net = EquivariantCNNCom2(initialize=False)
    a = torch.rand((16, 2, 128, 128))
    out = net(a)
    print(1)