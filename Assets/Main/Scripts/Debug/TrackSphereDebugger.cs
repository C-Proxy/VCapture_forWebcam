using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public class TrackSphereDebugger : MonoBehaviour
{
    [SerializeField]
    UdpReceiver m_UdpReceiver;
    [SerializeField]
    Transform m_LeftHandRoot, m_RightHandRoot, m_PoseRoot, m_LeftHandLineRoot, m_RightHandLineRoot;
    Transform[] m_LeftHandChildAnchors, m_RightHandChildAnchors, m_PoseChildAnchors;
    LineRenderer[] m_LeftHandLines, m_RightHandLines;
    int[][] m_VertexPairs = new int[][]{
        new[]{0,1,2,3,4},
        new[]{0,5,6,7,8},
        new[]{0,9,10,11,12},
        new[]{0,13,14,15,16},
        new[]{0,17,18,19,20},
    };
    private void Awake()
    {
        m_LeftHandChildAnchors = m_LeftHandRoot.GetChildren();
        m_RightHandChildAnchors = m_RightHandRoot.GetChildren();
        m_PoseChildAnchors = m_PoseRoot.GetChildren();

        m_LeftHandLines = m_LeftHandLineRoot.GetComponentsInChildren<LineRenderer>();
        m_RightHandLines = m_RightHandLineRoot.GetComponentsInChildren<LineRenderer>();

    }
    private void Start()
    {
        m_UdpReceiver.AssignCallback(ReceiveFunc);
    }
    private void Update()
    {
        WriteLine(true);
        WriteLine(false);
    }
    void ReceiveFunc(string label, Vector3[] points)
    {
        switch (label)
        {
            case "Left":
                ApplyPositions(m_LeftHandChildAnchors, points);
                break;
            case "Right":
                ApplyPositions(m_RightHandChildAnchors, points);
                break;
            case "Pose":
                ApplyPositions(m_PoseChildAnchors, points);
                break;
        }
    }
    void ApplyPositions(Transform[] anchors, Vector3[] points)
    {
        foreach (var (anchor, point) in anchors.Zip(points, (a, p) => (a, p)))
        {
            anchor.localPosition = point;
        }
    }
    void WriteLine(bool isLeft)
    {
        LineRenderer[] renderers;
        Transform[] anchors;
        if (isLeft)
        {
            renderers = m_LeftHandLines;
            anchors = m_LeftHandChildAnchors;
        }
        else
        {
            renderers = m_RightHandLines;
            anchors = m_RightHandChildAnchors;
        }
        foreach ((var renderer, var positions) in Enumerable.Range(0, 5)
            .Select(i =>
                (renderers[i], m_VertexPairs[i].Select(vertexId => anchors[vertexId].position).ToArray())
            )
        )
        {
            renderer.SetPositions(positions);
        }

    }
}
