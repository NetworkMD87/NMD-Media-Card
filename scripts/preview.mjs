import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../',import.meta.url));
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png'};
const server = createServer(async (request,response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    const relative = pathname === '/' ? 'demo/index.html' : pathname.slice(1);
    // Only serve public development files, never the private project handoff.
    if (!/^(demo\/|src\/|assets\/|tests\/browser\.html$|nmd-media-card\.js$)/.test(relative) || relative.includes('..') || relative.includes('\\')) {
      response.writeHead(404).end(); return;
    }
    const file = path.resolve(root,relative);
    if (!file.startsWith(root)) { response.writeHead(404).end(); return; }
    const data = await readFile(file);
    response.writeHead(200,{'Content-Type':types[path.extname(file)] || 'application/octet-stream','Cache-Control':'no-store'}).end(data);
  } catch { response.writeHead(404).end(); }
});
server.listen(Number(process.env.PORT) || 8767,'127.0.0.1',() => console.log(`NMD local sample preview: http://127.0.0.1:${server.address().port}/ (PID ${process.pid})`));
for (const signal of ['SIGINT','SIGTERM']) process.on(signal,() => server.close(() => process.exit(0)));
