using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace AISearchWindowsLauncher
{
    internal static class Program
    {
        private const string AppTitle = "AI Search Algorithm Visualizer";

        private static readonly Dictionary<string, string> ResourceMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "/", "index.html" },
            { "/index.html", "index.html" },
            { "/styles.css", "styles.css" },
            { "/favicon.png", "favicon.png" },
            { "/gif.worker.js", "gif.worker.js" },
            { "/Node.py", "Node.py" },
            { "/PriorityQueue.py", "PriorityQueue.py" },
            { "/SearchAgent.py", "SearchAgent.py" },
            { "/main.py", "main.py" },
            { "/docs/algorithm-guide.md", "docs/algorithm-guide.md" },
            { "/docs/api-reference.md", "docs/api-reference.md" },
            { "/docs/deployment-guide.md", "docs/deployment-guide.md" },
            { "/vendor/brython.min.js", "vendor/brython.min.js" },
            { "/vendor/brython_stdlib.js", "vendor/brython_stdlib.js" },
            { "/vendor/gif.js", "vendor/gif.js" },
            { "/vendor/jspdf.umd.min.js", "vendor/jspdf.umd.min.js" },
            { "/vendor/jszip.min.js", "vendor/jszip.min.js" },
            { "/vendor/lucide.min.js", "vendor/lucide.min.js" },
        };

        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            var port = FindFreePort();
            using (var server = new EmbeddedWebServer(port))
            using (var tray = new NotifyIcon())
            {
                server.Start();

                var url = "http://127.0.0.1:" + port + "/index.html";
                OpenBrowser(url);

                tray.Text = AppTitle;
                tray.Icon = SystemIcons.Application;
                tray.Visible = true;
                tray.ContextMenu = new ContextMenu(new[]
                {
                    new MenuItem("Open " + AppTitle, delegate { OpenBrowser(url); }),
                    new MenuItem("Exit", delegate { Application.Exit(); })
                });
                tray.ShowBalloonTip(2500, AppTitle, "The app is running locally. Use the tray icon to reopen or exit.", ToolTipIcon.Info);

                Application.Run();
                tray.Visible = false;
            }
        }

        private static int FindFreePort()
        {
            var listener = new TcpListener(IPAddress.Loopback, 0);
            listener.Start();
            var port = ((IPEndPoint)listener.LocalEndpoint).Port;
            listener.Stop();
            return port;
        }

        private static void OpenBrowser(string url)
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = url,
                UseShellExecute = true
            });
        }

        private sealed class EmbeddedWebServer : IDisposable
        {
            private readonly int port;
            private readonly TcpListener listener;
            private readonly Thread thread;
            private volatile bool running;

            public EmbeddedWebServer(int port)
            {
                this.port = port;
                listener = new TcpListener(IPAddress.Loopback, port);
                thread = new Thread(ListenLoop) { IsBackground = true };
            }

            public void Start()
            {
                running = true;
                listener.Start();
                thread.Start();
            }

            public void Dispose()
            {
                running = false;
                try { listener.Stop(); } catch { }
            }

            private void ListenLoop()
            {
                while (running)
                {
                    try
                    {
                        var client = listener.AcceptTcpClient();
                        ThreadPool.QueueUserWorkItem(delegate { HandleClient(client); });
                    }
                    catch
                    {
                        if (running)
                        {
                            Thread.Sleep(100);
                        }
                    }
                }
            }

            private static void HandleClient(TcpClient client)
            {
                using (client)
                using (var stream = client.GetStream())
                using (var reader = new StreamReader(stream, Encoding.ASCII, false, 8192, true))
                {
                    var requestLine = reader.ReadLine();
                    if (string.IsNullOrWhiteSpace(requestLine))
                    {
                        return;
                    }

                    string line;
                    while (!string.IsNullOrEmpty(line = reader.ReadLine())) { }

                    var parts = requestLine.Split(' ');
                    if (parts.Length < 2 || parts[0] != "GET")
                    {
                        WriteResponse(stream, 405, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Method not allowed"));
                        return;
                    }

                    var rawPath = parts[1].Split('?')[0];
                    var path = Uri.UnescapeDataString(rawPath);
                    string resourcePath;
                    if (!ResourceMap.TryGetValue(path, out resourcePath))
                    {
                        WriteResponse(stream, 404, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Not found"));
                        return;
                    }

                    var data = LoadResource(resourcePath);
                    if (data == null)
                    {
                        WriteResponse(stream, 404, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Resource not found"));
                        return;
                    }

                    WriteResponse(stream, 200, GetContentType(resourcePath), data);
                }
            }

            private static byte[] LoadResource(string resourcePath)
            {
                var assembly = Assembly.GetExecutingAssembly();
                var resourceName = "app." + resourcePath.Replace('/', '.');
                using (var stream = assembly.GetManifestResourceStream(resourceName))
                {
                    if (stream == null)
                    {
                        return null;
                    }

                    using (var memory = new MemoryStream())
                    {
                        stream.CopyTo(memory);
                        return memory.ToArray();
                    }
                }
            }

            private static void WriteResponse(NetworkStream stream, int statusCode, string contentType, byte[] body)
            {
                var statusText = statusCode == 200 ? "OK" : statusCode == 404 ? "Not Found" : "Method Not Allowed";
                var header = "HTTP/1.1 " + statusCode + " " + statusText + "\r\n" +
                             "Content-Type: " + contentType + "\r\n" +
                             "Content-Length: " + body.Length + "\r\n" +
                             "Cache-Control: no-store\r\n" +
                             "Connection: close\r\n\r\n";
                var headerBytes = Encoding.ASCII.GetBytes(header);
                stream.Write(headerBytes, 0, headerBytes.Length);
                stream.Write(body, 0, body.Length);
            }

            private static string GetContentType(string path)
            {
                var extension = Path.GetExtension(path).ToLowerInvariant();
                switch (extension)
                {
                    case ".html": return "text/html; charset=utf-8";
                    case ".css": return "text/css; charset=utf-8";
                    case ".js": return "application/javascript; charset=utf-8";
                    case ".py": return "text/plain; charset=utf-8";
                    case ".md": return "text/markdown; charset=utf-8";
                    case ".png": return "image/png";
                    default: return "application/octet-stream";
                }
            }
        }
    }
}
