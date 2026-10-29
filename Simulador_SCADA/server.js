/**
 * Servidor HTTP Local para el Simulador Electroneumático y SCADA Mecatrónico
 * UTN Facultad Regional Paraná — Mecatrónica II — Alumno: Hugo Ariel Martinez
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = process.env.PORT || 8085;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/' || reqPath === '') reqPath = '/index.html';

  const filePath = path.join(PUBLIC_DIR, reqPath);
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      return res.end('Archivo no encontrado');
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
    res.end(content);
  });
});

server.listen(PORT, () => {
  const url = `http://localhost:${PORT}`;
  console.log('======================================================================');
  console.log(' UTN FACULTAD REGIONAL PARANÁ — TECNICATURA SUPERIOR EN MECATRÓNICA');
  console.log(' Suite de Simulación Electroneumática y SCADA Clasificador ISA-101');
  console.log(' Alumno: Hugo Ariel Martinez · Cátedra: Mecatrónica II');
  console.log('----------------------------------------------------------------------');
  console.log(` Servidor activo en: ${url}`);
  console.log(' Presione Ctrl + C para detener el simulador.');
  console.log('======================================================================');

  if (process.argv.includes('--open')) {
    exec(`start "" "${url}"`);
  }
});
