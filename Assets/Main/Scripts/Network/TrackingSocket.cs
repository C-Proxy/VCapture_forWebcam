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

public class TrackingSocket : MonoBehaviour, ITrackObservable<PoseData>, ITrackObservable<HandData>
{
    [SerializeField]
    bool m_ShowText;
    [SerializeField]
    SocketSetting m_SocketSetting = new SocketSetting("localhost", 10800);
    UdpClient m_UdpClient;
    CancellationTokenSource m_ServerCTS;
    UnityEvent<string> m_Callback;
    UnityEvent<Vector3[]> m_PointsCallback, m_LeftHandCallback, m_RightHandCallback;
    UnityEvent<IReceivedData> m_ReceivedDataCallback;
    UnityEvent<PoseData> m_TrackingDataCallback;

    IConnectableUniTaskAsyncEnumerable<string> m_PackageSubject;
    public void Subscribe(Action<IUniTaskAsyncEnumerable<string>> subscription) => subscription(m_PackageSubject);
    IConnectableUniTaskAsyncEnumerable<PoseData> m_PoseSubject;
    public void Subscribe(Action<IUniTaskAsyncEnumerable<PoseData>> subscription) => subscription(m_PoseSubject);
    IConnectableUniTaskAsyncEnumerable<HandData> m_HandSubject;
    public void Subscribe(Action<IUniTaskAsyncEnumerable<HandData>> subscription) => subscription(m_HandSubject);


    private void Awake()
    {
        m_Callback = new UnityEvent<string>();
        m_PointsCallback = new UnityEvent<Vector3[]>();
        m_LeftHandCallback = new UnityEvent<Vector3[]>();
        m_RightHandCallback = new UnityEvent<Vector3[]>();
        m_ReceivedDataCallback = new UnityEvent<IReceivedData>();
        m_TrackingDataCallback = new UnityEvent<PoseData>();

        var packChannel = Channel.CreateSingleConsumerUnbounded<string>();
        m_PackageSubject = packChannel.Reader.ReadAllAsync().Publish();
        var packConnection = m_PackageSubject.Connect();
        var poseChannel = Channel.CreateSingleConsumerUnbounded<PoseData>();
        m_PoseSubject = poseChannel.Reader.ReadAllAsync().Publish();
        var poseConnection = m_PoseSubject.Connect();

        UniTask.Void(async () =>
        {
            await m_PackageSubject.ForEachAsync(str =>
           {
               var package = JsonUtility.FromJson<ReceivePackage>(str);
               var tag = package.Tag;
               var content = package.Content;
               switch (tag)
               {
                   case "PoseTransform":
                       poseChannel.Writer.TryWrite(JsonUtility.FromJson<PoseData>(content));
                       break;
                   // case "PosePosition":
                   //     m_PointsCallback.Invoke(JsonUtility.FromJson<LandmarkData>(content).landmarks);
                   //     break;
                   // case "LeftHandPosition":
                   //     m_LeftHandCallback.Invoke(JsonUtility.FromJson<LandmarkData>(content).landmarks);
                   //     break;
                   // case "RightHandPosition":
                   //     m_RightHandCallback.Invoke(JsonUtility.FromJson<LandmarkData>(content).landmarks);
                   //     break;
                   default:
                       Debug.Log($"Tag:{tag},Content:{content.ToString()}");
                       break;

               }
           }
            , gameObject.GetCancellationTokenOnDestroy());
            packConnection.Dispose();
        });
        var client = StartServer(m_SocketSetting);
        if (client == null)
            return;
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
            }).ForEachAsync(str => packChannel.Writer.TryWrite(str), cts.Token);
            packConnection.Dispose();

        });
    }
    UdpClient StartServer(SocketSetting setting)
    {
        if (m_ServerCTS != null)
        {
            Debug.LogWarning("Server has already started!");
            return null;
        }
        Debug.Log("Start Server.");
        return new UdpClient(setting.Port);

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
    public void AssignCallback_Pose(UnityAction<Vector3[]> callback) => m_PointsCallback.AddListener(callback);
    public void AssignCallback_LeftHand(UnityAction<Vector3[]> callback) => m_LeftHandCallback.AddListener(callback);
    public void AssignCallback_RightHand(UnityAction<Vector3[]> callback) => m_RightHandCallback.AddListener(callback);
    public void AssignCallback_Position(UnityAction<Vector3[]> callback, PositionTrackTag tag)
    {
        switch (tag)
        {
            case PositionTrackTag.Pose:
                AssignCallback_Pose(callback);
                break;
            case PositionTrackTag.LeftHand:
                AssignCallback_LeftHand(callback);
                break;
            case PositionTrackTag.RightHand:
                AssignCallback_RightHand(callback);
                break;
        }
    }

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