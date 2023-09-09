using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Linq;
using Tracking;

public class PoseRig : BasePoseRig<PoseData>
{
    [SerializeField]
    bool m_IsActive = true;
    [SerializeField, Range(0, 1)]
    PoseInfo m_PoseInfo = new PoseInfo(new Vector3[13]);
    HandInfo m_LeftHandInfo = new HandInfo(true, new Vector3[21]), m_RightHandInfo = new HandInfo(false, new Vector3[21]);
    public HandInfo LeftHandInfo => m_LeftHandInfo;
    public HandInfo RightHandInfo => m_RightHandInfo;
    public void SetLeftHand(Vector3[] points) => m_LeftHandInfo = HandInfo.Lerp(m_LeftHandInfo, points, m_Weight);
    public void SetRightHand(Vector3[] points) => m_RightHandInfo = HandInfo.Lerp(m_RightHandInfo, points, m_Weight);
    public void SetPose(Vector3[] datas) => m_PoseInfo = PoseInfo.Lerp(m_PoseInfo, new PoseInfo(datas), m_Weight);

    protected void Update()
    {
        if (!m_IsActive) return;

        m_HumanoidAnchor.Root.localRotation = m_PoseInfo.GetBodyRotation();
        m_HumanoidAnchor.LeftHand.SetLocalPositionAndRotation(m_PoseInfo.Hand_L, m_LeftHandInfo.GetHandRotation());
        m_HumanoidAnchor.RightHand.SetLocalPositionAndRotation(m_PoseInfo.Hand_R, m_RightHandInfo.GetHandRotation());
        m_HumanoidAnchor.LeftElbow.localPosition = m_PoseInfo.Elbow_L;
        m_HumanoidAnchor.RightElbow.localPosition = m_PoseInfo.Elbow_R;
        m_HumanoidAnchor.Head.SetLocalPositionAndRotation(m_PoseInfo.Nose, m_PoseInfo.GetHeadRotation());
    }
    [ContextMenu("Calibrate")]
    public void Calibrate()
    {
        Vector3 pos_LShoulder = m_PoseInfo.Shoulder_L, pos_RShoulder = m_PoseInfo.Shoulder_R;
        transform.localRotation = Quaternion.Inverse(Quaternion.LookRotation(Vector3.Cross(pos_RShoulder, pos_LShoulder), pos_LShoulder + pos_RShoulder));
        // m_HeadRig.localRotation = Quaternion.Inverse(m_PoseInfo.GetHeadRotation());
    }
    public struct PoseInfo
    {
        public Vector3[] Points;
        public Vector3 Nose => Points[0];
        public Vector3 Eye_L => Points[1];
        public Vector3 Eye_R => Points[2];
        public Vector3 Shoulder_L => Points[3];
        public Vector3 Shoulder_R => Points[4];
        public Vector3 Elbow_L => Points[5];
        public Vector3 Elbow_R => Points[6];
        public Vector3 Hand_L => Points[7];
        public Vector3 Hand_R => Points[8];
        public PoseInfo(Vector3[] points)
        {
            Points = points;
        }
        public static PoseInfo Lerp(PoseInfo info1, PoseInfo info2, float weight)
        => new PoseInfo(info1.Points.Zip(info2.Points, (p1, p2) => (p1, p2)).Select(_ => Vector3.Lerp(_.p1, _.p2, weight)).ToArray());

        public Quaternion GetHeadRotation()
        {
            var vec1 = Eye_L - Nose;
            var vec2 = Eye_R - Nose;
            return Quaternion.LookRotation(Vector3.Cross(vec2, vec1), vec1 + vec2);
        }
        public Quaternion GetBodyRotation()
        {
            Vector3 vecL = Shoulder_L, vecR = Shoulder_R;
            return Quaternion.LookRotation(Vector3.Cross(vecR, vecL), vecL + vecR);
        }
    }

    public struct HandInfo
    {
        public bool IsLeft;
        public Vector3[] Points;
        public Vector3 Wrist => Points[0];
        public Vector3[] Thumb => new[] { Points[1], Points[2], Points[3], Points[4] };
        public Vector3[] Index => new[] { Points[5], Points[6], Points[7], Points[8] };
        public Vector3[] Middle => new[] { Points[9], Points[10], Points[11], Points[12] };
        public Vector3[] Ring => new[] { Points[13], Points[14], Points[15], Points[16] };
        public Vector3[] Pinky => new[] { Points[17], Points[18], Points[19], Points[20] };

        public Vector3[][] GetFingerPoints() => new Vector3[][] { Thumb, Index, Middle, Ring, Pinky };
        public HandInfo(bool isLeft, Vector3[] points)
        {
            IsLeft = isLeft;
            Points = points;
        }
        public static HandInfo Lerp(HandInfo info1, Vector3[] points, float weight)
        => new HandInfo(info1.IsLeft, info1.Points.Zip(points, (p1, p2) => (p1, p2)).Select(_ => Vector3.Lerp(_.p1, _.p2, weight)).ToArray());
        public Quaternion GetHandRotation()
        {
            Vector3 wrist = Wrist, vec1 = Points[5] - wrist, vec2 = Points[17] - wrist;
            if (IsLeft)
                return Quaternion.LookRotation(vec1 + vec2, Vector3.Cross(vec2, vec1));
            else
                return Quaternion.LookRotation(vec1 + vec2, Vector3.Cross(vec1, vec2));
        }
        public Quaternion[][] GetFingerRotations(float ratio)
        {
            var wrist = Wrist;
            Vector3[] thumb = Thumb, index = Index, middle = Middle, ring = Ring, pinky = Pinky,
            d_t = new Vector3[] { thumb[1] - thumb[0], thumb[2] - thumb[1], thumb[3] - thumb[2] },
            d_i = new Vector3[] { index[0] - wrist, index[1] - index[0], index[2] - index[1], index[3] - index[2] },
            d_m = new Vector3[] { middle[0] - wrist, middle[1] - middle[0], middle[2] - middle[1], middle[3] - middle[2] },
            d_r = new Vector3[] { ring[0] - wrist, ring[1] - ring[0], ring[2] - ring[1], ring[3] - ring[2] },
            d_p = new Vector3[] { pinky[0] - wrist, pinky[1] - pinky[0], pinky[2] - pinky[1], pinky[3] - pinky[2] };
            Quaternion[][] result = Enumerable.Range(0, 5).Select(_ => new Quaternion[3]).ToArray();
            Vector3[] upwards;
            if (IsLeft)
            {
                upwards = new Vector3[]{
                    Vector3.Cross(index[0]-thumb[0],d_t[0]),
                    Vector3.Cross(d_m[0],d_i[0]),
                    Vector3.Cross(d_r[0],d_m[0]),
                    Vector3.Cross(d_p[0],d_r[0]),
                };
                // rr_t = Quaternion.LookRotation(d_t[0], Vector3.Cross(d_i[0], d_t[0]));
                // rr_i = Quaternion.LookRotation(d_i[0], Vector3.Cross(d_m[0], d_i[0]));
                // rr_m = Quaternion.LookRotation(d_m[0], Vector3.Cross(d_m[0], d_i[0]));
                // rr_r = Quaternion.LookRotation(d_r[0], Vector3.Cross(d_r[0], d_m[0]));
                // rr_p = Quaternion.LookRotation(d_p[0], Vector3.Cross(d_p[0], d_r[0]));
            }
            else
            {
                upwards = new Vector3[]{
                    Vector3.Cross(d_t[0],index[0]-thumb[0]),
                    Vector3.Cross(d_i[0],d_m[0]),
                    Vector3.Cross(d_m[0],d_r[0]),
                    Vector3.Cross(d_r[0],d_p[0]),
                };
                // rr_t = Quaternion.LookRotation(d_t[0], Vector3.Cross(d_t[0], d_i[0]));
                // rr_i = Quaternion.LookRotation(d_i[0], Vector3.Cross(d_i[0], d_m[0]));
                // rr_m = Quaternion.LookRotation(d_m[0], Vector3.Cross(d_i[0], d_m[0]));
                // rr_r = Quaternion.LookRotation(d_r[0], Vector3.Cross(d_m[0], d_r[0]));
                // rr_p = Quaternion.LookRotation(d_p[0], Vector3.Cross(d_r[0], d_p[0]));
            }
            return new Quaternion[][] {
                    GetThumbRot(d_t,ratio),
                    GetFingerRots(upwards[1],d_i,ratio),
                    GetFingerRots(upwards[2],d_m,ratio),
                    GetFingerRots(upwards[2],d_r,ratio),
                    GetFingerRots(upwards[3],d_p,ratio),
        };
        }
        Quaternion[] GetThumbRot(bool isLeft, Quaternion baseRot, Vector3[] deltaPos, MyUnityExtension.RotAxis offset)
        {
            var length = deltaPos.Length;
            var result = new Quaternion[length];
            result[0] = baseRot;
            for (int i = 1; i < length; i++)
            {
                var cross = Vector3.Cross(deltaPos[i], deltaPos[i - 1]);
                if (cross.sqrMagnitude < Mathf.Epsilon)
                    result[i] = result[i - 1];
                else
                    result[i] = Quaternion.LookRotation(deltaPos[i], cross).RotateAxis(offset);
            }
            return result;
        }
        Quaternion[] GetThumbRot(Vector3[] deltaPos, float ratio)
        {
            var right = Vector3.Cross(deltaPos[0], deltaPos[1]) + Vector3.Cross(deltaPos[1], deltaPos[2]);
            return new Quaternion[]{
                Quaternion.LookRotation(deltaPos[0],right).RotateAxis(MyUnityExtension.RotAxis.Z270),
                Quaternion.LookRotation(deltaPos[1],right).RotateAxis(MyUnityExtension.RotAxis.Z270),
                Quaternion.LookRotation(deltaPos[2],right).RotateAxis(MyUnityExtension.RotAxis.Z90),
            };
        }
        Quaternion[] GetFingerRots(bool isLeft, Quaternion baseRot, Vector3[] deltaPos, MyUnityExtension.RotAxis offset)
        {
            var length = deltaPos.Length;
            var result = new Quaternion[length - 1];
            Vector3 cross;
            for (int i = 0; i < length - 1; i++)
            {
                cross = Vector3.Cross(deltaPos[i + 1], -deltaPos[i]);
                if (cross.sqrMagnitude < Mathf.Epsilon)
                {
                    if (i == 0)
                        result[i] = baseRot;
                    else
                        result[i] = result[i - 1];
                }
                else
                {
                    result[i] = Quaternion.LookRotation(deltaPos[i + 1], cross).RotateAxis(MyUnityExtension.RotAxis.Z270).RotateAxis(offset);
                }
            }
            return result;
        }
        Quaternion[] GetFingerRots(Vector3 handUp, Vector3[] delta, float ratio)
        {
            // return new Quaternion[] {
            //     Quaternion.LookRotation(delta[1], delta[0]),
            //     Quaternion.LookRotation(delta[2], delta[1]),
            //     Quaternion.LookRotation(delta[3], delta[2]),
            // };
            var right = Vector3.Lerp(Vector3.Cross(handUp, delta[0]), Vector3.Cross(delta[2], -delta[1]) + Vector3.Cross(delta[3], -delta[2]), ratio);
            return new Quaternion[]{
                Quaternion.LookRotation(delta[1],right).RotateAxis(MyUnityExtension.RotAxis.Z270),
                Quaternion.LookRotation(delta[2],right).RotateAxis(MyUnityExtension.RotAxis.Z270),
                Quaternion.LookRotation(delta[3],right).RotateAxis(MyUnityExtension.RotAxis.Z270),
            };
        }
    }
}