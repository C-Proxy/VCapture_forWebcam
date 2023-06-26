using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public class PointSphere : MonoBehaviour
{
    GameObject[] m_Spheres;
    [SerializeField, Range(0, 1000)]
    float Ratio;
    [SerializeField, Range(0, 10000)]
    float XYRatio;

    void Start()
    {
        m_Spheres = new GameObject[this.transform.childCount];

        for (int i = 0; i < this.transform.childCount; i++)
        {
            m_Spheres[i] = this.transform.GetChild(i).gameObject;
        }
    }

    public void MovePoint(Vector3[] points)
    {
        foreach (var (point, sphere) in Enumerable.Zip(points, m_Spheres, (p, g) => (p, g)))
        {
            sphere.transform.localPosition = point * Ratio;
        }
    }
}