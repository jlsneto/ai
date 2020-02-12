using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AIClient : MonoBehaviour
{
    public static AIClient instance;

    [SerializeField]
    private string ip = "127.0.0.1";
    [SerializeField]
    private int port = 9999;

    public Transform cube;

    private AIClientChannel channel;
    private Dictionary<string, AIAgent> agents;

    private bool isConnected;

    private void Awake()
    {
        instance = this;
    }

    // Start is called before the first frame update
    void Start()
    {
        channel = new AIClientChannel(ip, port);
        channel.onConnected += OnConnected;
        channel.onMessage += OnMessage;
    }

    public void AddAgent(AIAgent agent)
    {
        if(agents == null) agents = new Dictionary<string, AIAgent>();
        agents.Add(agent.id, agent);
    }

    private void OnMessage(AIObjectReceiveModel data)
    {
        agents[data.agentId].OnMessage(data);
    }

    private void OnConnected()
    {
        isConnected = true;
    }

    public void Send(AIObjectSendModel data)
    {
        if (isConnected)
        {
            channel.SendMessage(data);
        }
    }
}
