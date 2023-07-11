using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Tracking;

public class BasePoseRig : MonoBehaviour, IPoseControlable
{
    public HumanoidAnchor HumanoidAnchor => m_HumanoidAnchor;
    [SerializeField]
    HumanoidAnchor m_HumanoidAnchor = default;
    TrackingData m_TrackingData;
    TrackingData m_TargetData;
    [SerializeField, Range(0f, 1f)]
    float m_Weight = 0.5f;
    private void Start()
    {
        m_TrackingData = m_TargetData = TrackingData.identiy;
    }
    private void Update()
    {
        m_TrackingData = TrackingData.Lerp(m_TrackingData, m_TargetData, m_Weight);
        m_HumanoidAnchor.Apply(m_TrackingData);
    }
    public void ApplyPose(TrackingData data) => m_TargetData = data;

}
