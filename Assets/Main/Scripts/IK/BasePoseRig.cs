using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System.Threading;

using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;
using Tracking;
using IK;

public abstract class BasePoseRig<T> : MonoBehaviour, IPoseObserver, IPoseRig
where T : IReceivedData
{
    public HumanoidAnchor HumanoidAnchor => m_HumanoidAnchor;
    [SerializeField]
    protected HumanoidAnchor m_HumanoidAnchor = default;
    [SerializeField, Range(0f, 1f)]
    protected float m_Weight = 0.5f;

    public void CreateSubscription(IUniTaskAsyncEnumerable<PoseData> observable)
    {
        UniTask.Void(async () =>
        {
            await observable.Pairwise().ForEachAsync(pair =>
            {
                var (pre, cur) = pair;
                m_HumanoidAnchor.Apply(PoseData.Lerp(pre, cur, m_Weight));
            }, gameObject.GetCancellationTokenOnDestroy());
        });
    }
}