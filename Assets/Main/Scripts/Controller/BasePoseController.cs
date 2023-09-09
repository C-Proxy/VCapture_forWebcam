using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Tracking;

using Cysharp.Threading.Tasks;

public abstract class BasePoseController<T> : MonoBehaviour
where T : IReceivedData
{
    [SerializeField] protected TrackingSocket m_Source;
    protected virtual void Start()
    {
        var target = this.GetComponent<ITrackObserver<PoseData>>();
        m_Source.Subscribe(subject => target.CreateSubscription(subject));
    }
}
