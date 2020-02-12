using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AIAgent : MonoBehaviour
{

    public string id;
    public Transform target;
    private AIObjectSendModel data;
    public float speed = 10;
    private State state = State.IDLE;
    private BotControlScript bot;

    // Start is called before the first frame update
    void Start()
    {
        bot = GetComponent<BotControlScript>();
        AIClient.instance.AddAgent(this);
        data = new AIObjectSendModel();
        data.agentId = id;
    }

    public void OnMessage(AIObjectReceiveModel message)
    {
        state = message.state;
    }

    // Update is called once per frame
    void Update()
    {
        bot.h = 0;
        bot.v = 0;
        switch (state)
        {
            case State.FOWARD: bot.v = 1; break;
            case State.BACK: bot.v = -1; break;
            case State.LEFT: bot.h = -1; break;
            case State.RIGHT: bot.h = 1; break;
        }

        data.distance = Vector3.Distance(transform.position, target.position);
        AIClient.instance.Send(data);
    }
}
