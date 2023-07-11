using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System.Threading;

namespace Tracking
{
    [Serializable]
    public struct TrackingData
    {
        public TransformData Head, LeftHand, RightHand, Root;
        public PositionData LeftElbow, RightElbow;

        public static TrackingData identiy => new TrackingData(TransformData.identity, TransformData.identity, TransformData.identity, TransformData.identity, PositionData.identity, PositionData.identity);
        public TrackingData(TransformData head, TransformData leftHand, TransformData rightHand, TransformData root, PositionData leftElbow, PositionData rightElbow)
        {
            Head = head;
            LeftHand = leftHand;
            RightHand = rightHand;
            Root = root;
            LeftElbow = leftElbow;
            RightElbow = rightElbow;
        }
        public static TrackingData Lerp(TrackingData a, TrackingData b, float w)
        => new TrackingData(
            TransformData.Lerp(a.Head, b.Head, w),
            TransformData.Lerp(a.LeftHand, b.LeftHand, w),
            TransformData.Lerp(a.RightHand, b.RightHand, w),
            TransformData.Lerp(a.Root, b.Root, w),
            PositionData.Lerp(a.LeftElbow, b.LeftElbow, w),
            PositionData.Lerp(a.RightElbow, b.RightElbow, w)
            );

        public override string ToString() => $"Head:{Head.ToString()}";

        public (TransformData, TransformData, TransformData, TransformData, PositionData, PositionData) GetTuple()
        => (Head, LeftHand, RightHand, Root, LeftElbow, RightElbow);

        [Serializable]
        public struct TransformData : IPosition, IRotation
        {
            [SerializeField]
            Vector3 position;
            [SerializeField]
            Quaternion rotation;
            public Vector3 Position => position;
            public Quaternion Rotation => rotation;
            public static TransformData identity => new TransformData(Vector3.zero, Quaternion.identity);
            public TransformData(Vector3 pos, Quaternion rot)
            {
                position = pos;
                rotation = rot;
            }
            public override string ToString() => $"Pos:{position.ToString()},Rot:{rotation.ToString()}";
            public static TransformData Lerp(TransformData a, TransformData b, float w) => new TransformData(Vector3.Lerp(a.position, b.position, w), Quaternion.Lerp(a.rotation, b.rotation, w));
        }
        [Serializable]
        public struct PositionData : IPosition
        {
            [SerializeField]
            Vector3 position;
            public Vector3 Position => position;
            public static PositionData identity => new PositionData(Vector3.zero);
            public PositionData(Vector3 pos)
            {
                position = pos;
            }

            public override string ToString() => $"Pos:{position.ToString()}";
            public static PositionData Lerp(PositionData a, PositionData b, float w) => new PositionData(Vector3.Lerp(a.position, b.position, w));
        }
    }
    public struct AllTrackingData
    {
        public Vector3[] landmarks;
    }
    public interface IPoseControlable
    {
        HumanoidAnchor HumanoidAnchor { get; }
        void ApplyPose(TrackingData data);
    }
}