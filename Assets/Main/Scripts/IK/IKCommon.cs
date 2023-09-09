using System;
using UnityEngine;
using Tracking;

namespace IK
{
    public interface IPoseRig
    {
        public HumanoidAnchor HumanoidAnchor { get; }
    }
    public interface IHandRig
    {

    }
    [Serializable]
    public struct HumanoidAnchor
    {
        public Transform Head, LookTarget, LeftHand, RightHand, LeftElbow, RightElbow, Root;
        public void Apply(PoseData data)
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