using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System.Threading;
using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;


namespace Tracking
{
    public interface IReceivedData { }
    [Serializable]
    public struct PoseData : IReceivedData
    {
        public TransformData Head, LeftHand, RightHand, Root;
        public PositionData LeftElbow, RightElbow;

        public static PoseData identiy => new PoseData(TransformData.identity, TransformData.identity, TransformData.identity, TransformData.identity, PositionData.identity, PositionData.identity);
        public PoseData(TransformData head, TransformData leftHand, TransformData rightHand, TransformData root, PositionData leftElbow, PositionData rightElbow)
        {
            Head = head;
            LeftHand = leftHand;
            RightHand = rightHand;
            Root = root;
            LeftElbow = leftElbow;
            RightElbow = rightElbow;
        }
        public static PoseData Lerp(PoseData a, PoseData b, float w)
        => new PoseData(
            TransformData.Lerp(a.Head, b.Head, w),
            TransformData.Lerp(a.LeftHand, b.LeftHand, w),
            TransformData.Lerp(a.RightHand, b.RightHand, w),
            TransformData.Lerp(a.Root, b.Root, w),
            PositionData.Lerp(a.LeftElbow, b.LeftElbow, w),
            PositionData.Lerp(a.RightElbow, b.RightElbow, w)
            );
        // public TrackingData Lerp(TrackingData target, float weight) => TrackingData.Lerp(this, target, weight);

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
        // public struct RotationData : IRotation
        // {
        //     [SerializeField]
        //     Quaternion rotation;
        //     public Quaternion Rotation => rotation;
        //     public static RotationData identity => new RotationData(Quaternion.identity);
        //     public RotationData(Quaternion rot)
        //     {
        //         rotation = rot;
        //     }
        //     public static RotationData Lerp(RotationData a, RotationData b, float w) => new RotationData(Quaternion.Slerp(a.rotation, b.rotation, w));
        // }
    }
    public struct LandmarkData : IReceivedData
    {
        public Vector3[] landmarks;
    }
    public struct HandData : IReceivedData
    {
        public bool IsLeft;
        public Quaternion[][] Rotations;
        public static HandData Lerp(HandData a, HandData b, float w) { return default; }
    }
    public interface ITrackObserver<T>
    where T : IReceivedData
    {
        public void CreateSubscription(IUniTaskAsyncEnumerable<T> observable);
    }
    public interface IPoseObserver : ITrackObserver<PoseData>
    {
        // HumanoidAnchor HumanoidAnchor { get; }
    }
    public interface IHandObserver : ITrackObserver<HandData>
    {

    }
    public interface IHolisticObserver : IPoseObserver, IHandObserver { }
    public interface ITrackObservable<T>
    where T : IReceivedData
    {
        void Subscribe(Action<IUniTaskAsyncEnumerable<T>> subscription);
    }



    public enum PositionTrackTag { Pose, LeftHand, RightHand }
}