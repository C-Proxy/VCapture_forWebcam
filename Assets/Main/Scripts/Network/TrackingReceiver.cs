using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

using Tracking;

using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;

public class TrackingReceiver : BaseTrackingSource
{
    [SerializeField]
    bool m_ShowText;
    [SerializeField]
    SocketSetting m_SocketSetting = new SocketSetting("localhost", 10800);
    UdpClient m_UdpClient;
    CancellationTokenSource m_ServerCTS;
    UnityEvent<string> m_Callback;
    UnityEvent<Vector3[]> m_PointsCallback;

    private void Awake()
    {
        m_Callback = new UnityEvent<string>();
        m_PointsCallback = new UnityEvent<Vector3[]>();
        m_TrackingCallback = new UnityEvent<TrackingData>();

        // m_Callback.AddListener(str =>
        // {
        //     if (str == null || str == "0")
        //     {
        //         Debug.LogWarning("Received Empty");
        //         return;
        //     }
        //     Debug.Log(str);
        //     ReceiveInfo info = JsonUtility.FromJson<ReceiveInfo>(str);
        //     m_PointsCallback.Invoke(info.Label, info.Points);
        // });
        m_Callback.AddListener(str =>
        {
            var package = JsonUtility.FromJson<ReceivePackage>(str);
            var tag = package.Tag;
            var content = package.Content;
            switch (package.Tag)
            {
                case "IK":
                    m_TrackingCallback.Invoke(JsonUtility.FromJson<TrackingData>(content));
                    break;
                case "Pose":
                    m_PointsCallback.Invoke(JsonUtility.FromJson<AllTrackingData>(content).landmarks);
                    break;

            }
        });
        StartServer(m_SocketSetting);
    }
    void StartServer(SocketSetting setting)
    {
        if (m_ServerCTS != null)
        {
            Debug.LogWarning("Server has already started!");
            return;
        }
        Debug.Log("Start Server.");
        var client = new UdpClient(setting.Port);
        var cts = new CancellationTokenSource();
        m_ServerCTS = cts;
        UniTask.Void(async () =>
        {
            await UniTaskAsyncEnumerable.Create<string>(async (writer, token) =>
            {
                try
                {
                    while (true)
                    {
                        token.ThrowIfCancellationRequested();
                        var result = await client.ReceiveAsync();
                        var text = Encoding.UTF8.GetString(result.Buffer);
                        if (m_ShowText)
                            Debug.Log(text);
                        await writer.YieldAsync(text);
                    }
                }
                catch (Exception e) when (!(e is OperationCanceledException))
                {
                    Debug.LogException(e);
                }
                finally
                {
                    StopServer();
                }
            }).ForEachAsync(str => m_Callback.Invoke(str), cts.Token);
        });
    }
    void StopServer()
    {
        if (m_UdpClient == null)
            return;
        m_UdpClient?.Close();
        m_UdpClient = null;
        Debug.Log("Server Closed.");
    }
    void OnDestroy()
    {
        StopServer();
    }
    void OnApplicationQuit()
    {
        StopServer();
    }

    public void AssignCallback(UnityAction<string> callback) => m_Callback.AddListener(callback);
    public void AssignCallback(UnityAction<Vector3[]> callback) => m_PointsCallback.AddListener(callback);
    // public void AssignCallback(UnityAction<TrackingData> callback) => m_TrackingCallback.AddListener(callback);

    [Serializable]
    struct SocketSetting
    {
        [SerializeField]
        string m_Host;
        [SerializeField]
        int m_Port;

        public string Host => m_Host;
        public int Port => m_Port;


        public SocketSetting(string host, int port)
        {
            m_Host = host;
            m_Port = port;
        }

    }
    [Serializable]
    struct ReceivePackage
    {
        [SerializeField] string tag;
        public string Tag => tag;
        [SerializeField] string content;
        public string Content => content;
    }
}

public abstract class BaseTrackingSource : MonoBehaviour
{
    protected UnityEvent<TrackingData> m_TrackingCallback;
    public void AssignCallback(UnityAction<TrackingData> callback) => m_TrackingCallback.AddListener(callback);

}