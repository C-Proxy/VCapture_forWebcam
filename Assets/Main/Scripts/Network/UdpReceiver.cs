using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

using Cysharp.Threading.Tasks;
using Cysharp.Threading.Tasks.Linq;

public class UdpReceiver : MonoBehaviour
{
    [SerializeField]
    bool m_DebugMode;
    [SerializeField]
    SocketSetting m_SocketSetting = new SocketSetting("localhost", 10800);
    UdpClient m_UdpClient;
    CancellationTokenSource m_ServerCTS;
    UnityEvent<string> m_Callback;
    UnityEvent<string, Vector3[]> m_PointsCallback;

    private void Awake()
    {
        m_Callback = new UnityEvent<string>();
        m_PointsCallback = new UnityEvent<string, Vector3[]>();
        m_Callback.AddListener(str =>
        {
            if (str == null || str == "0")
            {
                Debug.LogWarning("Received Empty");
                return;
            }
            Debug.Log(str);
            ReceiveInfo info = JsonUtility.FromJson<ReceiveInfo>(str);
            m_PointsCallback.Invoke(info.Label, info.Points);
        });
        // m_Callback.AddListener(str => Debug.Log(str));
        StartServer(m_SocketSetting);
    }
    void StartServer(SocketSetting setting)
    {
        if (m_ServerCTS != null)
        {
            Debug.LogWarning("Server has already started!");
            return;
        }
        var port = setting.Port;
        Debug.Log("Start Server.");
        var client = new UdpClient(port);
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
                        var text = Encoding.ASCII.GetString(result.Buffer);
                        if (m_DebugMode)
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

    public void AssignCallback(UnityAction<string> method) => m_Callback.AddListener(method);
    public void AssignCallback(UnityAction<string, Vector3[]> method) => m_PointsCallback.AddListener(method);

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
}
