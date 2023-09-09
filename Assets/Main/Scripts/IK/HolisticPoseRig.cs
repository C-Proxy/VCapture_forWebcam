using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;

using Tracking;

public class HolisticPoseRig : BasePoseRig<PoseData>, IHolisticObserver
{
    HandData m_HandData, m_Target;

    public void CreateSubscription(IUniTaskAsyncEnumerable<HandData> observable)
    {
        UniTask.Void(async () =>
        {
            await observable.Pairwise().ForEachAsync(pair =>
            {
                var (pre, cur) = pair;
            }, gameObject.GetCancellationTokenOnDestroy());
        });
    }

}
