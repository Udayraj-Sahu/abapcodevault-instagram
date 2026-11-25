import { init, render, events } from './reel.js';
const g = document.getElementById('c').getContext('2d');
await Promise.all([400, 500, 600, 700].flatMap(w => [`${w} 40px Inter`, `${w} 40px InterTight`, `${w} 40px JBMono`]).map(f => document.fonts.load(f)));
const Q = new URLSearchParams(location.search);
const spec = await (await fetch(Q.get('spec') || 'jobs/reel.json')).json();
window.DUR = init(spec);
window.EV = events();
window.render = t => render(g, t);
window.READY = true;
