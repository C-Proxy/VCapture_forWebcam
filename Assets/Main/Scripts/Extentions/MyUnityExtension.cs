using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public static class MyUnityExtension
{
    public static void SetLocalPositionAndRotation(this Transform transform, Vector3 position, Quaternion rotation)
    {
        transform.localPosition = position;
        transform.localRotation = rotation;
    }
    public static Transform[] GetChildren(this Transform transform) => Enumerable.Range(0, transform.childCount).Select(i => transform.GetChild(i)).ToArray();
    public static Transform[][] GetFingerBones(this Animator animator, bool isLeft)
    {
        if (isLeft)
            return new Transform[][]{
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.LeftThumbProximal),
                animator.GetBoneTransform(HumanBodyBones.LeftThumbIntermediate),
                animator.GetBoneTransform(HumanBodyBones.LeftThumbDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.LeftIndexProximal),
                animator.GetBoneTransform(HumanBodyBones.LeftIndexIntermediate),
                animator.GetBoneTransform(HumanBodyBones.LeftIndexDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.LeftMiddleProximal),
                animator.GetBoneTransform(HumanBodyBones.LeftMiddleIntermediate),
                animator.GetBoneTransform(HumanBodyBones.LeftMiddleDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.LeftRingProximal),
                animator.GetBoneTransform(HumanBodyBones.LeftRingIntermediate),
                animator.GetBoneTransform(HumanBodyBones.LeftRingDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.LeftLittleProximal),
                animator.GetBoneTransform(HumanBodyBones.LeftLittleIntermediate),
                animator.GetBoneTransform(HumanBodyBones.LeftLittleDistal),
            },
        };
        else
            return new Transform[][]{
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.RightThumbProximal),
                animator.GetBoneTransform(HumanBodyBones.RightThumbIntermediate),
                animator.GetBoneTransform(HumanBodyBones.RightThumbDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.RightIndexProximal),
                animator.GetBoneTransform(HumanBodyBones.RightIndexIntermediate),
                animator.GetBoneTransform(HumanBodyBones.RightIndexDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.RightMiddleProximal),
                animator.GetBoneTransform(HumanBodyBones.RightMiddleIntermediate),
                animator.GetBoneTransform(HumanBodyBones.RightMiddleDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.RightRingProximal),
                animator.GetBoneTransform(HumanBodyBones.RightRingIntermediate),
                animator.GetBoneTransform(HumanBodyBones.RightRingDistal),
            },
            new Transform[]{
                animator.GetBoneTransform(HumanBodyBones.RightLittleProximal),
                animator.GetBoneTransform(HumanBodyBones.RightLittleIntermediate),
                animator.GetBoneTransform(HumanBodyBones.RightLittleDistal),
            },
        };


    }

    public static Quaternion RotateAxis(this Quaternion rot, RotAxis axis)
    {
        float x = rot.x, y = rot.y, z = rot.z, w = rot.w;
        return axis switch
        {
            RotAxis.None => rot,
            RotAxis.X90 => new Quaternion(w + x, z + y, z - y, w - x),
            RotAxis.Y90 => new Quaternion(x - z, w + y, x + z, w - y),
            RotAxis.Z90 => new Quaternion(y + x, y - x, w + z, w - z),
            RotAxis.X270 => new Quaternion(x - w, y - z, y + z, x + w),
            RotAxis.Y270 => new Quaternion(z + x, y - w, z - x, y + w),
            RotAxis.Z270 => new Quaternion(x - y, x + y, z - w, z + w),
            RotAxis.X180 => new Quaternion(w, z, -y, -x),
            RotAxis.Y180 => new Quaternion(-z, w, x, -y),
            RotAxis.Z180 => new Quaternion(y, -x, w, -z),
            _ => default
        };
    }

    public enum RotAxis
    {
        None, X90, Y90, Z90, X180, Y180, Z180, X270, Y270, Z270
    }
}