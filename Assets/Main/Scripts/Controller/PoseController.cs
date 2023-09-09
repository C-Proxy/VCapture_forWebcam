using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Tracking;

[RequireComponent(typeof(ITrackObserver<PoseData>))]
public class PoseController : BasePoseController<PoseData> { }
