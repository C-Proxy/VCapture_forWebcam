using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

[RequireComponent(typeof(Animator))]
public class IKControl : MonoBehaviour
{
    [SerializeField]
    MyUnityExtension.RotAxis m_Axis, m_Axis2;
    [SerializeField, Range(0, 1)]
    float m_Ratio;
    Animator m_Animator;
    [SerializeField] bool m_IsActive = true;
    [SerializeField] PoseRig m_PoseRig;
    Transform m_BodyTarget, m_HeadTarget, m_LeftHandTarget, m_RightHandTarget, m_LeftElbowTarget, m_RightElbowTarget, m_LookTarget;
    Transform m_HeadBone, m_NeckBone, m_LeftHandBone, m_RightHandBone;
    Transform[][] m_LeftFingerBones, m_RightFingerBones;
    private void Awake()
    {
        m_Animator = GetComponent<Animator>();
        var targets = m_PoseRig.HumanoidAnchor;
        m_BodyTarget = targets.Root;
        m_HeadTarget = targets.Head;
        m_LookTarget = targets.LookTarget;
        m_LeftHandTarget = targets.LeftHand;
        m_RightHandTarget = targets.RightHand;
        m_LeftElbowTarget = targets.LeftElbow;
        m_RightElbowTarget = targets.RightElbow;


        m_HeadBone = m_Animator.GetBoneTransform(HumanBodyBones.Head);
        m_NeckBone = m_Animator.GetBoneTransform(HumanBodyBones.Neck);
        m_LeftHandBone = m_Animator.GetBoneTransform(HumanBodyBones.LeftHand);
        m_RightHandBone = m_Animator.GetBoneTransform(HumanBodyBones.RightHand);

        m_LeftFingerBones = m_Animator.GetFingerBones(true);
        m_RightFingerBones = m_Animator.GetFingerBones(false);
    }
    private void OnAnimatorIK(int layerIndex)
    {
        if (!m_IsActive)
            return;

        transform.SetPositionAndRotation(m_BodyTarget.position, m_BodyTarget.rotation);

        m_Animator.SetLookAtWeight(1);
        m_Animator.SetLookAtPosition(m_LookTarget.position);

        m_Animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 1);
        m_Animator.SetIKRotationWeight(AvatarIKGoal.LeftHand, 1);
        m_Animator.SetIKHintPositionWeight(AvatarIKHint.LeftElbow, 1);
        m_Animator.SetIKHintPosition(AvatarIKHint.LeftElbow, m_LeftElbowTarget.position);
        m_Animator.SetIKPosition(AvatarIKGoal.LeftHand, m_LeftHandTarget.position);
        m_Animator.SetIKRotation(AvatarIKGoal.LeftHand, m_LeftHandTarget.rotation);

        m_Animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
        m_Animator.SetIKRotationWeight(AvatarIKGoal.RightHand, 1);
        m_Animator.SetIKHintPositionWeight(AvatarIKHint.RightElbow, 1);
        m_Animator.SetIKHintPosition(AvatarIKHint.RightElbow, m_RightElbowTarget.position);
        m_Animator.SetIKPosition(AvatarIKGoal.RightHand, m_RightHandTarget.position);
        m_Animator.SetIKRotation(AvatarIKGoal.RightHand, m_RightHandTarget.rotation);

    }
    private void LateUpdate()
    {
        ApplyFingerRotation(m_BodyTarget.rotation, m_LeftFingerBones, m_PoseRig.LeftHandInfo.GetFingerRotations(m_Ratio));
        ApplyFingerRotation(m_BodyTarget.rotation, m_RightFingerBones, m_PoseRig.RightHandInfo.GetFingerRotations(m_Ratio));
        Vector3 headAng = m_HeadBone.eulerAngles, neckAng = m_NeckBone.eulerAngles;
        float ang = Mathf.DeltaAngle(360.0f, m_HeadTarget.eulerAngles.z);
        headAng.z = ang;
        neckAng.z = ang * 0.5f;
        m_HeadBone.eulerAngles = headAng;
        m_NeckBone.eulerAngles = neckAng;


    }
    void ApplyFingerRotation(Quaternion centerRot, Transform[][] fingers, Quaternion[][] fingerRots)
    {
        foreach (var (finger, rot) in fingers.SelectMany(_ => _).Zip(fingerRots.SelectMany(_ => _), (f, r) => (f, r)))
        {
            finger.rotation = centerRot * rot.RotateAxis(m_Axis).RotateAxis(m_Axis2);
        }
    }
}
