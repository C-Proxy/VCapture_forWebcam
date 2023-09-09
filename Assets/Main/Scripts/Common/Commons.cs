using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace Tracking
{
    public interface IPosition
    {
        public Vector3 Position { get; }
        public static Vector3 Lerp;
    }
    public interface IRotation
    {
        public Quaternion Rotation { get; }
        public static Quaternion Lerp;
    }

}
