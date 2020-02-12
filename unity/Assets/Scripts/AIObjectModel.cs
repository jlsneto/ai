using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum State
{
    IDLE,
    FOWARD,
    BACK,
    LEFT,
    RIGHT,
}

public class AIObjectSendModel
{
    public string agentId;
    public float distance;
    
}

public class AIObjectReceiveModel {
    public string agentId;
    public State state;
}
