import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Resvg } from '@resvg/resvg-js';
import { alphaTab } from './adapter.mjs';

// Render the GP-imported model. Rasterization executes alphaTab SVG output;
// it does not inspect, normalize, or reconstruct the source images.
export function renderImported(score, directory, {start=1,count=score.masterBars.length,width=1400,barsPerRow=3,prefix='score'}={}) {
    fs.mkdirSync(directory,{recursive:true});
    const settings=new alphaTab.Settings();settings.core.engine='svg';
    settings.display.startBar=start;settings.display.barCount=count;
    settings.display.barsPerRow=barsPerRow;settings.display.staveProfile=alphaTab.StaveProfile.Tab;
    settings.notation.rhythmMode=alphaTab.TabRhythmMode.ShowWithBars;
    const renderer=new alphaTab.rendering.ScoreRenderer(settings);renderer.width=width;
    const chunks=[];let error;
    renderer.error.on(e=>{error=e;});
    renderer.partialLayoutFinished.on(r=>renderer.renderResult(r.id));
    renderer.partialRenderFinished.on(r=>{if(typeof r.renderResult==='string')chunks.push(r);});
    renderer.renderScore(score,[0]);
    if(error)throw error;
    if(!chunks.length)throw new Error('alphaTab produced no SVG chunks');
    const font=fileURLToPath(import.meta.resolve('@coderline/alphatab/font/Bravura.otf'));
    const outputs=[];
    const fontFiles=[font,...['arial.ttf','arialbd.ttf','ariali.ttf','georgia.ttf','georgiai.ttf','georgiab.ttf']
        .map(name=>path.join(process.env.WINDIR??'C:/Windows','Fonts',name)).filter(p=>fs.existsSync(p))];
    for(const [i,chunk] of chunks.entries()) {
        const basename=`${prefix}_${String(i+1).padStart(3,'0')}`;
        // BrowserUiFacade normally supplies this music-font CSS. Standalone
        // SVGs must carry it themselves. usvg does not expand CSS font shorthand,
        // so expand the renderer's explicit declarations mechanically.
        const svg=chunk.renderResult.replace(/font:([^;]+);/g,(_,value)=>{
            const match=value.match(/(?:(italic)\s+)?(?:(bold)\s+)?([\d.]+)px\s+(.+)/);
            if(!match)throw new Error(`Unsupported SVG font declaration ${value}`);
            return `font-family:${match[4]};font-size:${match[3]}px;font-style:${match[1]??'normal'};font-weight:${match[2]??'normal'};`;
        }).replace(/(<svg[^>]*>)/,`$1<style>.at {font-family:Bravura;font-size:${settings.display.resources.engravingSettings.musicFontSize}px;font-style:normal;font-weight:normal;}</style>`);
        fs.writeFileSync(path.join(directory,basename+'.svg'),svg);
        const png=new Resvg(svg,{background:'white',font:{fontFiles,loadSystemFonts:true,defaultFontFamily:'Arial'}}).render().asPng();
        fs.writeFileSync(path.join(directory,basename+'.png'),png);
        outputs.push({image:basename+'.png',svg:basename+'.svg',width:chunk.width,height:chunk.height,
            x:chunk.x,y:chunk.y,first_master_bar:chunk.firstMasterBarIndex,last_master_bar:chunk.lastMasterBarIndex});
    }
    fs.writeFileSync(path.join(directory,prefix+'_render.json'),JSON.stringify(outputs,null,2)+'\n');
    return outputs;
}
