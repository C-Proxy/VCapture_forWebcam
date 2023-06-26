using System;
using System.Threading;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;
using Cysharp.Threading.Tasks.Triggers;

public class Test : MonoBehaviour
{
    CancellationTokenSource m_TestTokenSource;
    void Start()
    {
        // Application.wantsToQuit += Quit;
        UniTask.Void(async () =>
        {
            m_TestTokenSource = new CancellationTokenSource();
            await UniTaskAsyncEnumerable.Create<string>(async (writer, token) =>
            {
                try
                {
                    while (true)
                    {
                        token.ThrowIfCancellationRequested();
                        await writer.YieldAsync("test");
                        await UniTask.Delay(1000);
                    }
                }
                finally
                {
                    Debug.Log("Exit.");
                    await CountAsync("Exit", 5);
                    // Application.wantsToQuit -= Quit;
                    Debug.Log("Done!");
                }
            }).ForEachAsync(str => Debug.Log(str), m_TestTokenSource.Token);
        });


    }
    void Quit()
    {
        StopAsync().Forget();
    }
    public void Stop() => StopAsync().Forget();
    async UniTask StopAsync()
    {
        if (!m_TestTokenSource.Token.IsCancellationRequested)
        {
            m_TestTokenSource?.Cancel();
            await CountAsync("Stop", 3);
            Debug.Log("Closed");
        }
        else
        {
            Debug.Log("Already Canceled.");
        }
    }
    async UniTask CountAsync(string name, int cnt)
    {
        for (var i = 0; i < cnt; i++)
        {
            Debug.Log(String.Format("{0}:{1}", name, i));
            await UniTask.Delay(1000);
        }
    }
    // private void OnApplicationQuit()
    // {
    //     Debug.Log("CancelQuit");
    //     Application.CancelQuit();
    //     StopAsync().Forget();
    // }

}
