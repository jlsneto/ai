using Battlehub.Dispatcher;
using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class AIClientChannel
{

    public Action onConnected;
    public Action<AIObjectReceiveModel> onMessage;

    private string ip;
    private int port;
    private TcpClient client;
    private NetworkStream stream;
    private StreamReader readerStream;
    private StreamWriter writerStream;
    public AIClientChannel(string ip, int port)
    {
        this.ip = ip;
        this.port = port;
        Thread t = new Thread(Init);
        t.IsBackground = true;
        t.Start();
    }

    public void Init()
    {
        Debug.Log("Conectando ...");
        client = new TcpClient();
        client.Connect(ip, port);

        Debug.Log("Conectado!");

        stream = client.GetStream();
        writerStream = new StreamWriter(stream);
        readerStream = new StreamReader(stream);

        Dispatcher.Current.BeginInvoke(() =>
        {
            if (onConnected != null) onConnected.Invoke();
        });

        MessageListener();
    }

    private void MessageListener()
    {
        Debug.Log("Listener iniciado");
        while (stream.CanRead)
        {

            string input = readerStream.ReadLine();
            Debug.Log("Recebido: " + input);
            AIObjectReceiveModel received = JsonUtility.FromJson<AIObjectReceiveModel>(input);

            Dispatcher.Current.BeginInvoke(() =>
            {
                if (onMessage != null) onMessage.Invoke(received);
            });


        }
    }

    public void SendMessage(AIObjectSendModel data)
    {
        string stringfyied = JsonUtility.ToJson(data);
        writerStream.WriteLine(stringfyied);
    }
}
