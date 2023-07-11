using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Tracking;

public class PoseController : MonoBehaviour
{
    [SerializeField] TrackingReceiver m_Source;
    [SerializeField] BasePoseRig m_Target;
    void Start()
    {
        m_Source.AssignCallback(m_Target.ApplyPose);
    }
}
