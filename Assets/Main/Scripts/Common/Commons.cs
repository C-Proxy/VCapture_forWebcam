using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace Tracking
{
    public interface IPosition
    {
        public Vector3 Position { get; }
        public static Vector3 Lerp;
    }
    public interface IRotation
    {
        public Quaternion Rotation { get; }
        public static Quaternion Lerp;
    }
    public interface ITrackingSource
    {
        public void AssignCallback(UnityAction<TrackingData> callback);

    }
    [Serializable]
    public struct HumanoidAnchor
    {
        public Transform Head, LookTarget, LeftHand, RightHand, LeftElbow, RightElbow, Root;
        public void Apply(TrackingData data)
        {
            var (head, leftHand, rightHand, root, leftElbow, rightElbow) = data.GetTuple();
            Head.SetLocalPositionAndRotation(head.Position, head.Rotation);
            LeftHand.SetLocalPositionAndRotation(leftHand.Position, leftHand.Rotation);
            RightHand.SetLocalPositionAndRotation(rightHand.Position, rightHand.Rotation);
            Root.SetLocalPositionAndRotation(root.Position, root.Rotation);

            LeftElbow.localPosition = leftElbow.Position;
            RightElbow.localPosition = rightElbow.Position;


        }
    }
}
