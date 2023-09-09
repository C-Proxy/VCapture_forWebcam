using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Tracking;

public class HolisticController : MonoBehaviour
{
    [SerializeField] TrackingSocket m_Source;
    void Start()
    {
        var target = this.GetComponent<IHolisticObserver>();
        var pose = (ITrackObserver<PoseData>)target;
        var hand = (ITrackObserver<HandData>)target;

        m_Source.Subscribe(subject => pose.CreateSubscription(subject));
        m_Source.Subscribe(subject => hand.CreateSubscription(subject));
    }
}
