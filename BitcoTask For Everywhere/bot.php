<?php
error_reporting(E_ALL & ~E_DEPRECATED);
$API_KEY=$curl=null;
$UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36';
define('AK',__DIR__.'/BASkey.txt');

function gc(){global $curl;if(!$curl){$curl=curl_init();curl_setopt_array($curl,[CURLOPT_COOKIEFILE=>__DIR__.'/cookies.txt',CURLOPT_COOKIEJAR=>__DIR__.'/cookies.txt',CURLOPT_RETURNTRANSFER=>true,CURLOPT_HEADER=>false,CURLOPT_CONNECTTIMEOUT=>30,CURLOPT_TIMEOUT=>30,CURLOPT_FOLLOWLOCATION=>true,CURLOPT_MAXREDIRS=>5,CURLOPT_ENCODING=>'',CURLOPT_SSL_VERIFYPEER=>false,CURLOPT_SSL_VERIFYHOST=>false]);}return $curl;}
function rq($m,$u,$d=null,$h=[],$r=null,$j=false,$f=true){$ch=gc();curl_setopt_array($ch,[CURLOPT_URL=>$u,CURLOPT_FOLLOWLOCATION=>$f,CURLOPT_CUSTOMREQUEST=>strtoupper($m)]);$x=$r?['Referer:'.$r]:[];if(strtoupper($m)==='POST'){$b=$j&&is_array($d)?json_encode($d):(is_array($d)?http_build_query($d):$d);if($j&&is_array($d))$x[]='Content-Type:application/json';elseif(is_array($d))$x[]='Content-Type:application/x-www-form-urlencoded;charset=UTF-8';curl_setopt_array($ch,[CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>$b]);}else curl_setopt_array($ch,[CURLOPT_POST=>false,CURLOPT_POSTFIELDS=>null]);curl_setopt($ch,CURLOPT_HTTPHEADER,array_merge($x,$h));for($i=0;$i<2;$i++){$rs=curl_exec($ch);if($rs!==false)break;if($i<1)usleep(500000);}return[$rs,curl_error($ch),curl_getinfo($ch)];}
function uj($b,$r){if(preg_match('#^[a-z][a-z0-9+.-]*://#i',$r))return $r;$p=parse_url($b);$s=$p['scheme']??'https';$h=$p['host']??'';$pt=isset($p['port'])?':'.$p['port']:'';if(strpos($r,'/')===0)return"$s://$h$pt$r";$d=str_replace('\\','/',dirname($p['path']??'/'));return"$s://$h$pt".rtrim($d,'/')."/$r";}
function pb64($p,$w,$h){if(empty($p))return'';$r=base64_decode($p);if(!$r)return'';$i=imagecreatetruecolor($w,$h);if(!$i)return'';imagealphablending($i,false);imagesavealpha($i,true);$b=unpack('C*',$r);if(!$b){imagedestroy($i);return'';}$bi=1;for($n=0,$t=$w*$h;$n<$t;$n++){$x=$n%$w;$y=(int)($n/$w);$cr=$b[$bi++]??0;$cg=$b[$bi++]??0;$cb=$b[$bi++]??0;$ca=$b[$bi++]??0;$c=($w<64&&$ca<100)?imagecolorallocatealpha($i,255,255,255,127):imagecolorallocatealpha($i,$cr,$cg,$cb,127-(int)(($ca*127)/255));imagesetpixel($i,$x,$y,$c);}ob_start();imagepng($i);$r=base64_encode(ob_get_clean());imagedestroy($i);return $r;}

function asolve($m,$o,$d,$q=false){global $API_KEY;$mb=pb64($m,200,100);$ob=[];foreach($o as $i=>$v)$ob[]=pb64($v,$d[$i][0]??32,$d[$i][1]??32);$ob=array_pad($ob,8,'');$b='https://bypassallshortlinks.space';$ch=curl_init($b.'/in.php');curl_setopt_array($ch,[CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>['key'=>$API_KEY,'method'=>'bitcotasks_select','main'=>$mb,'options'=>json_encode($ob)],CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>30,CURLOPT_CONNECTTIMEOUT=>30,CURLOPT_SSL_VERIFYPEER=>false,CURLOPT_SSL_VERIFYHOST=>false]);$rs=curl_exec($ch);curl_close($ch);if($rs===false){if(!$q)echo"  ├─ ⚠️ API timeout\n";return[null,null];}$tid=null;if(preg_match('/^OK\|(.+)$/s',trim($rs),$m))$tid=trim($m[1]);else{$j=json_decode($rs,true);if($j&&!empty($j['request']))$tid=$j['request'];}if(!$tid){if(!$q)echo"  ├─ ❌ API: ".substr(trim($rs),0,60)."\n";return[null,null];}for($i=0;$i<40;$i++){sleep(3);$p=curl_init($b.'/res.php?key='.urlencode($API_KEY).'&action=get&id='.urlencode($tid).'&json=1');curl_setopt_array($p,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>15,CURLOPT_SSL_VERIFYPEER=>false,CURLOPT_SSL_VERIFYHOST=>false]);$pr=curl_exec($p);curl_close($p);if($pr===false)continue;$pr=trim($pr);if(preg_match('/^OK\|(.+)$/s',$pr,$m))return[trim($m[1]),null];$pd=json_decode($pr,true);if(!$pd)continue;if(isset($pd['status'])&&$pd['status']==1){$r=$pd['request']??null;if(is_string($r))return[trim($r),null];return[null,null];}$r=$pd['request']??'';if(strpos($r,'ERROR')!==false){if(!$q)echo"  ├─ ❌ $r\n";return[null,null];}}if(!$q)echo"  ├─ ⏱️ API timeout\n";return[null,null];}
function aclick($img,$q=false){global $API_KEY;if(preg_match('#^data:image/[^;]+;base64,(.+)$#s',$img,$m))$img=$m[1];$b='https://bypassallshortlinks.space';$ch=curl_init($b.'/in.php');curl_setopt_array($ch,[CURLOPT_POST=>true,CURLOPT_POSTFIELDS=>['key'=>$API_KEY,'method'=>'bitcotasks_click','image'=>$img],CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>30,CURLOPT_CONNECTTIMEOUT=>30,CURLOPT_SSL_VERIFYPEER=>false,CURLOPT_SSL_VERIFYHOST=>false]);$rs=curl_exec($ch);curl_close($ch);if($rs===false){if(!$q)echo"  ├─ ⚠️ Click fail\n";return[null,null];}$tid=null;if(preg_match('/^OK\|(.+)$/s',trim($rs),$m))$tid=trim($m[1]);else{$j=json_decode($rs,true);if($j&&!empty($j['request']))$tid=$j['request'];}if(!$tid){if(!$q)echo"  ├─ ❌ Click err\n";return[null,null];}for($i=0;$i<40;$i++){sleep(3);$p=curl_init($b.'/res.php?key='.urlencode($API_KEY).'&action=get&id='.urlencode($tid).'&json=1');curl_setopt_array($p,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>15,CURLOPT_SSL_VERIFYPEER=>false,CURLOPT_SSL_VERIFYHOST=>false]);$pr=curl_exec($p);curl_close($p);if($pr===false)continue;$pr=trim($pr);if(preg_match('/^OK\|(.+)$/s',$pr,$m)){$c=array_map('intval',explode(',',trim($m[1],'[] ')));if(count($c)>=2)return[$c[0],$c[1]];return[null,null];}$pd=json_decode($pr,true);if(!$pd)continue;if(isset($pd['status'])&&$pd['status']==1){$c=$pd['request']??null;if(is_string($c)){$c=array_map('intval',explode(',',trim($c,'[] ')));if(count($c)>=2)return[$c[0],$c[1]];}elseif(is_array($c)&&count($c)>=2)return[(int)$c[0],(int)$c[1]];return[null,null];}$r=$pd['request']??'';if(strpos($r,'ERROR')!==false){if(!$q)echo"  ├─ ❌ $r\n";return[null,null];}}if(!$q)echo"  ├─ ⏱️ Click timeout\n";return[null,null];}
function spow($c,$d){if(empty($c))return null;$p=str_repeat('0',(int)$d);for($n=0;$n<2e6;$n++){$h=hash('sha256',"$c:$n");if(strncmp($h,$p,strlen($p))===0)return['nonce'=>$n,'hash'=>$h];}return null;}

function ejp($js){
  $fn1=$fv=$fn2=$s=$t=$pe=$ve=null;
  if(preg_match('/var\s+payload\s*=\s*"([^"]+)"/',$js,$m)){[$a,$b]=explode('&',$m[1]);if(!$b)return null;[$fn1,$fv]=explode('=',$a,2);$fn2=explode('=',$b)[0];}
  else{if(!preg_match('/var\s+payload\s*=\s*"([^=]+)=([^&]+)&([^=]+)="/',$js,$m))return null;$fn1=$m[1];$fv=$m[2];$fn2=$m[3];}
  if(preg_match('/if\s*\(response\.([A-Za-z0-9]+)\)/',$js,$m))$s=$m[1];
  elseif(preg_match('/if\s*\(\s*response\s*\.\s*([A-Za-z0-9]+)/',$js,$m))$s=$m[1];
  elseif(preg_match('/\.([A-Za-z0-9]{4,})\s*===?\s*true/',$js,$m))$s=$m[1];
  if(!$s)return null;
  if(preg_match('/value\s*=\s*response\.([A-Za-z0-9]+)/',$js,$m))$t=$m[1];
  elseif(preg_match('/token\s*=\s*response\.([A-Za-z0-9]+)/',$js,$m))$t=$m[1];
  elseif(preg_match('/\.\s*([A-Za-z0-9]{4,})\s*\)\s*\{[^}]*?token/i',$js,$m))$t=$m[1];
  if(!$t)return null;
  if(preg_match('#fetch\("(/captcha2/[^"]+)"#',$js,$m))$pe=$m[1];
  elseif(preg_match("#fetch\('(/captcha2/[^']+)'#",$js,$m))$pe=$m[1];
  if(!$pe)return null;
  if(preg_match('/xhr\.open\("POST",\s*"([^"]+)"/',$js,$m))$ve=$m[1];
  elseif(preg_match("/xhr\.open\('POST',\s*'([^']+)'/",$js,$m))$ve=$m[1];
  elseif(preg_match('/\.open\s*\(\s*"POST"\s*,\s*"([^"]+)"/',$js,$m))$ve=$m[1];
  if(!$ve)return null;
  return[$fn1,$fv,$fn2,$s,$t,$pe,$ve];
}

function timer($s){for($i=$s;$i>=1;$i--){echo"\r\033[K  ├─ ⏳ ".str_pad($i,2,' ',STR_PAD_LEFT)."s...";flush();if($i>1)sleep(1);}echo"\r\033[K  ├─ Viewed ✅\n";flush();}

function saveCap($img,$info=''){global $UA;$dir=__DIR__.'/captchas';if(!is_dir($dir))mkdir($dir,0777,true);$fn=$dir.'/cap_'.date('Ymd_His').'_'.mt_rand(1000,9999).'.gif';
  if(preg_match('#^data:image/[^;]+;base64,(.+)$#s',$img,$m))$img=$m[1];
  $raw=base64_decode($img);if($raw){file_put_contents($fn,$raw);if($info)file_put_contents($fn.'.txt',$info);}
}
function scap($url,$html,$q=false,$retry=1){global $UA;
  for($attempt=0;$attempt<=$retry;$attempt++){
    if($attempt>0){if(!$q)echo"  ├─ 🔄 Retry attempt $attempt...\n";sleep(2);}
    if(!preg_match('/src="(\/captcha2\/[^"]+\.js\?[^"]+)"/',$html,$m)){if(!$q)echo"  ├─ ❌ No captcha JS\n";return false;}
    $h=['User-Agent:'.$UA];
    [$j,$e]=rq('GET',uj($url,$m[1]),null,$h,$url);
    if($e){if(!$q)echo"  ├─ ❌ JS fail\n";continue;}
    $p=ejp($j);
    if(!$p){if(!$q)echo"  ├─ ❌ Params fail\n";continue;}
    [$fn1,$fv,$fn2,$s,$t,$pe,$ve]=$p;
    [$cd,$e]=rq('POST',uj($url,$pe),['t'=>(int)(microtime(true)*1e3),'r'=>mt_rand()/mt_getrandmax()],array_merge($h,['Content-Type:application/json']),$url,true);
    if($e){if(!$q)echo"  ├─ ❌ Data fail\n";continue;}
    $d=json_decode($cd,true);
    if(!$d){if(!$q)echo"  ├─ ❌ Parse fail\n";continue;}
    if(!empty($d['error'])){
      $err=$d['error'];
      if($err==='rate_limited'){if(!$q)echo"  ├─ ⏱️ Rate limited, waiting ".($d['retryAfter']??60)."s\n";sleep($d['retryAfter']??60);continue;}
      if($err==='busy'&&$attempt<$retry){if(!$q)echo"  ├─ ⚠️ Busy, retrying\n";sleep(rand(1,3));continue;}
      if(!$q)echo"  ├─ ❌ API: $err\n";continue;
    }
    if(empty($d['image'])&&empty($d['options'])){if(!$q)echo"  ├─ ❌ No captcha data\n";continue;}
    $cm=!empty($d['image'])&&empty($d['options']);$sl=null;$sel=null;
    $cimg=$cm?($d['image']??''):($d['pixel']??'');
    if($cm){[$cx,$cy]=aclick($d['image'],$q);if($cx===null){if(!$q)echo"  ├─ ❌ Solve fail\n";continue;}$sel=[$cx,$cy];}
    else{$opx=array_map(fn($o)=>$o['pixels']??'',$d['options']??[]);$odm=array_map(fn($o)=>[$o['width']??32,$o['height']??32],$d['options']??[]);[$sl]=asolve($d['pixel']??'',$opx,$odm,$q);if($sl===null){if(!$q)echo"  ├─ ❌ Solve fail\n";continue;}}
    $vp=[$fn1=>$fv,$fn2=>json_encode($cm?$sel:[(int)$sl])];
    [$vb,$e]=rq('POST',uj($url,$ve),http_build_query($vp),array_merge($h,['Content-Type:application/x-www-form-urlencoded']),$url);
    if($e){if(!$q)echo"  ├─ ❌ Val fail\n";continue;}
    $r=json_decode($vb,true);
    if(!$r){if(!$q)echo"  ├─ ❌ Val parse fail\n";continue;}
    $ok=false;
    if(!empty($r[$s])){$tk=$r[$t]??null;if($tk)$ok=true;}
    if(!$ok){foreach($r as$k=>$v)if($v===true){$s=$k;break;}if(!empty($r[$s])){$tk=$r[$t]??null;if($tk)$ok=true;}}
    $info="answer:".json_encode($cm?$sel:[(int)$sl])."\nresponse:".json_encode($r)."\ntype:".($cm?'click':'select')."\nresult:".($ok?'success':'fail');
    if($cimg)saveCap($cimg,$info);
    if($ok)return$tk;
    if(!$q)echo"  ├─ ❌ Val err\n";
  }
  return false;
}

function ev($html){$v=['token'=>null,'hash'=>null,'sub_id'=>null,'key'=>null];foreach(['token','hash','sub_id','key','api_key']as$k){$dk=$k==='api_key'?'key':$k;if(preg_match(sprintf('/(?:var|let|const)\s+%s\s*=\s*[\'"]([^\'"]+)[\'"]/',$k),$html,$m))$v[$dk]=$m[1];if(!$v[$dk]&&preg_match(sprintf('/data-%s\s*=\s*[\'"]([^\'"]+)[\'"]/',str_replace('_','-',$k)),$html,$m))$v[$dk]=$m[1];if(!$v[$dk]&&preg_match(sprintf('/"%s"\s*:\s*"([^"]+)"/',$k),$html,$m))$v[$dk]=$m[1];}return$v;}

function pal($pg,$url,$n,$t,$ti,$rw,$q=false,$retry=1){global $UA;
  for($attempt=0;$attempt<=$retry;$attempt++){
    if($attempt>0){if(!$q)echo"  ├─ 🔄 Retry captcha...\n";sleep(2);}
    $v=ev($pg);if(!$v['token']||!$v['hash']||!$v['sub_id']||!$v['key']){if(!$q)echo"  ├─ ❌ Missing vars\n";return false;}
    $ct=null;
    if(preg_match('/var\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/',$pg,$m))$ct=$m[1];
    if(!$ct&&preg_match('/const\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/',$pg,$m))$ct=$m[1];
    if(!$ct&&preg_match('/let\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/',$pg,$m))$ct=$m[1];
    if(!$ct&&preg_match_all('/<input[^>]+type\s*=\s*["\']hidden["\'][^>]*name\s*=\s*["\']([^"\']+)["\']/i',$pg,$ms)){foreach($ms[1]as$n2){if(stripos($n2,'captcha')!==false||stripos($n2,'token')!==false||stripos($n2,'ctn')!==false||stripos($n2,'crtk')!==false){$ct=$n2;break;}}if(!$ct&&!empty($ms[1]))$ct=end($ms[1]);}
    if(!$ct){if(!$q)echo"  ├─ ❌ No ctn field\n";return false;}
    $tk=scap($url,$pg,$q,2);if(!$tk){if(!$q)echo"  ├─ ❌ Captcha fail\n";continue;}
    rq('POST',$url,['action'=>'start_view'],['X-Requested-With: XMLHttpRequest','Origin:https://bitcotasks.com','User-Agent:'.$UA],$url);
    if(preg_match('/var (?:duration|timer)\s*=\s*(\d+(?:\s*[-+]\s*\d+)*);/',$pg,$m)){$dur=eval('return '.$m[1].';');timer($dur);}
    else{if(!$q)echo"  ├─ ⏳ Waiting 5s...\n";sleep(5);}
    $ad=['hash'=>$v['hash'],'sub_id'=>$v['sub_id'],'key'=>$v['key'],'token'=>$v['token'],'action'=>'proccessLead',$ct=>$tk];
    [$b,$e]=rq('POST','https://bitcotasks.com/system/ajax.php',$ad,['User-Agent:'.$UA,'Content-Type:application/x-www-form-urlencoded; charset=UTF-8','Origin:https://bitcotasks.com','X-Requested-With:XMLHttpRequest'],$url);
    if($e){if(!$q)echo"  ├─ ❌ Lead err\n";return false;}
    $r=json_decode($b,true);if(!$r){if(!$q)echo"  ├─ ❌ Lead parse\n";return false;}
    if(($r['status']??0)==200){echo"  ├─ ✅ ".strip_tags($r['message']??"+$rw")."\n";return true;}
    $msg=strip_tags($r['message']??'');
    if(stripos($msg,'captcha')!==false||stripos($msg,'invalid')!==false||stripos($msg,'expired')!==false){
      if(!$q)echo"  ├─ ⚠️ $msg — retrying\n";continue;
    }
    echo"  ├─ ❌ ".substr($msg,0,100)."\n";return false;
  }
  if(!$q)echo"  ├─ ❌ All retries failed\n";return false;
}

function cw($p,$c,$w){$s=mb_strlen($c);return $p.$c.str_repeat(' ',max(0,$w-mb_strlen($p)-$s))."│\n";}
function tr($t,$m){return mb_strlen($t)<=$t ? $t : mb_substr($t,0,$m-1)."…";}
function ptc($tk,$ad,$bu,$n=1,$t=1){global $UA;$w=54;$ti=$ad['title']??'Unknown';$rw=$ad['reward']??'0';
  echo "╭".str_repeat('─',$w)."╮\n";
  echo cw("│ 🚀 AD $n/$t","",$w);
  echo "├".str_repeat('─',$w)."┤\n";
  echo cw("│ 📌 ",tr($ti,$w-4),$w);
  echo cw("│ 💰 ",tr($rw,$w-4),$w);
  $ok=false;
  for($attempt=0;$attempt<3;$attempt++){
    if($attempt>0){echo cw("│  ","▶ Re-fetching view URL...",$w);sleep(rand(2,4));}
    echo "\r\033[K";echo cw("│  ","▶ Init...",$w);
    [$b,$e]=rq('POST',$bu,['hash'=>$ad['hash'],'sid'=>$ad['sid']??'','key'=>$ad['key'],'type'=>'ptc','token'=>$tk,'action'=>'init_transaction'],['X-Requested-With: XMLHttpRequest','Origin:https://bitcotasks.com','User-Agent:'.$UA],$bu);
    if($e)continue;
    $rs=json_decode($b,true);
    if(!$rs||($rs['status']??0)===999||!isset($rs['offer']))continue;
    $au=$rs['offer'];
    echo "\r\033[K";echo cw("│ ","▶ Init ✅",$w);echo cw("│  ","▶ Load...",$w);
    [$pg,$e2]=rq('GET',$au,null,['Accept:text/html','Accept-Language:en-GB,en;q=0.9','User-Agent:'.$UA],$bu);
    if($e2)continue;
    echo "\r\033[K";echo cw("│ ","▶ Load ✅",$w);
    $ok=pal($pg,$au,$n,$t,$ti,$rw);
    if($ok)break;
  }
  $s=$ok?'✅ DONE':'❌ FAILED';
  echo ($ok?"\r\033[K".cw("│ ","▶ Done ✅",$w):"").cw("│ ",tr($s,$w-2),$w)."╰".str_repeat('─',$w)."╯\n\n";
  return$ok;
}
function ploop($tk,$as,$bu){$sc=0;$fa=[];foreach($as as$i=>$a){$n=$i+1;if($i>0){$dl=rand(3,5);echo"\n  ├─ ⏳ Waiting {$dl}s before next ad...\n";sleep($dl);}echo"\n--- Ad $n/".count($as)." ---\n";if(ptc($tk,$a,$bu,$n,count($as)))$sc++;else $fa[]=$a;}return[$sc,$fa];}
function eks($u){$p=parse_url($u);$k=$s=null;if(isset($p['query'])){parse_str($p['query'],$q);$k=$q['key']??null;$s=$q['sub_id']??null;}if(!$k||!$s){$pp=explode('/',trim($p['path']??'', '/'));if(count($pp)>=3&&$pp[0]==='offerwall'){$k=$pp[1];$s=$pp[2];}}return[$k,$s];}

function fwBypass($ui,$bd,$h1,$maxRetry=2){
  for($attempt=0;$attempt<=$maxRetry;$attempt++){
    if($attempt>0){echo"  ├─ 🔄 Re-fetching page...\n";sleep(2);}
    $fu=null;$r2=null;
    if(strpos($ui,'firewall.php')!==false){
      $fu=$ui;[$fb,$e]=rq('GET',$fu,null,$h1);
      if($e){echo"❌ Fail: $e\n";continue;}
      $r2=$fb;
    }else{
      [$r1,$e]=rq('GET',$ui,null,$h1,null,false,false);
      if($e){echo"❌ Fail\n";continue;}
      if(!preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/",$r1,$m)){echo"❌ No redirect\n";return null;}
      [$r2,$e]=rq('GET',$m[1],null,$h1,$ui);
      if($e){echo"❌ Redir fail\n";continue;}
      $fu=$m[1];
    }
    if(!preg_match('/src="(\/captcha2\/[^"]+\.js\?[^"]+)"/',$r2,$m)){echo"❌ No JS\n";continue;}
    if(!preg_match('/const\s+captchaTokenName\s*=\s*"([^"]+)"/',$r2,$m)){echo"❌ No ctn\n";continue;}
    $ctn=$m[1];
    $tk=scap($fu,$r2,false,2);
    if(!$tk){echo"❌ Captcha fail\n";continue;}
    echo"  ✅ Solved\n";
    [$vr,$e]=rq('POST',$fu,['action'=>'validate',$ctn=>$tk],$h1);
    if($e){echo"❌ Val fail\n";continue;}
    $vj=json_decode($vr,true);
    $ou=null;
    if($vj&&($vj['status']??'')==='success'&&!empty($vj['redirect']))$ou=uj($bd,$vj['redirect']);
    if(!$ou&&preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/",$vr,$m))$ou=uj($bd,$m[1]);
    if(!$ou){echo"❌ No redirect\n";continue;}
    return $ou;
  }
  return null;
}

function main(){
  global $argv,$UA;
  $ia=isset($argv)&&count($argv)>1&&!empty($argv[1]);
  if(!$ia){system(strncasecmp(PHP_OS,'WIN',3)===0?'cls':'clear');$w=54;$bt="BITCOTASKS BOT";echo"╭".str_repeat('─',$w)."╮\n│ $bt".str_repeat(' ',max(0,$w-2-mb_strlen($bt)))."│\n╰".str_repeat('─',$w)."╯\n\n";}
  if(file_exists(AK)){$c=trim(file_get_contents(AK));if($c){global $API_KEY;$API_KEY=$c;echo"✅ Key loaded\n";}}else{echo"🔑 Enter key: ";global $API_KEY;$API_KEY=trim(fgets(STDIN));if(!$API_KEY){echo"❌ Exit\n";return;}file_put_contents(AK,$API_KEY);}
  $ui=$ia?trim($argv[1]):null;if(!$ui){echo"Link: ";$ui=trim(fgets(STDIN));}if(!$ui){echo"❌ No link\n";return;}
  if(strpos($ui,'view/')!==false){echo"📌 Direct PTC\n";$h=['User-Agent:'.$UA,'Accept:text/html','Accept-Language:en-GB,en;q=0.9'];[$b,$e]=rq('GET',$ui,null,$h,null,false,false);if($e){echo"❌ Fail\n";return;}$lu=null;if(preg_match("/window\.location\.href\s*=\s*'([^']+)'/",$b,$m))$lu=$m[1];elseif(preg_match('/window\.location\.href\s*=\s*"([^"]+)"/',$b,$m))$lu=$m[1];if(!$lu){echo"❌ No redirect\n";return;}$lu=uj($ui,$lu);[$lp,$e]=rq('GET',$lu,null,$h,$ui);if($e){echo"❌ Fail\n";return;}$ti='PTC Ad';if(preg_match('/<title>([^<]+)<\/title>/i',$lp,$m))$ti=trim($m[1]);pal($lp,$lu,1,1,$ti,'0',false);return;}
  $pd=parse_url($ui);$bd=$pd['scheme'].'://'.$pd['host'];[$bk,$si]=eks($ui);if(!$bk||!$si){echo"❌ No key/sub_id\n";return;}
  echo"📌 Key:$bk Sub:$si\n\n🛡️ Firewall\n";
  $h1=['User-Agent:'.$UA,'Accept:text/html','Accept-Language:en-GB,en;q=0.9'];
  $ou=fwBypass($ui,$bd,$h1);if(!$ou){echo"❌ Firewall bypass failed\n";return;}
  [$ob,$e]=rq('GET',$ou,null,$h1);if($e){echo"❌ OW fail\n";return;}
  $ot=null;if(preg_match("/var\s+token\s*=\s*'([^']+)'/",$ob,$m))$ot=$m[1];if(!$ot){echo"❌ No OW token\n";return;}
  echo"\n🚀 PTC offers...\n";
  [$sb,$e]=rq('POST',$ou,['token'=>$ot,'action'=>'switch_cat','type'=>'ptc'],array_merge($h1,['Content-Type:application/x-www-form-urlencoded','Origin:https://bitcotasks.com','X-Requested-With:XMLHttpRequest']),$ou);if($e){echo"❌ Switch fail\n";return;}
  $pt=json_decode($sb,true);if(!$pt){echo"❌ JSON err\n";return;}
  $as=$pt['items']??[];echo"✅ ".count($as)." ads found\n".str_repeat('=',54)."\n";
  [$sc,$fa]=ploop($ot,$as,$ou);
  if($fa){echo"\n🔄 Retry ".count($fa)." failed\n";sleep(2);[$rs2,$sf]=ploop($ot,$fa,$ou);$sc+=$rs2;}
  $w=54;$ss="✅ $sc/".count($as)." completed";echo"\n╭".str_repeat('─',$w)."╮\n│ $ss".str_repeat(' ',max(0,$w-2-mb_strlen($ss)))."│\n╰".str_repeat('─',$w)."╯\n\n";
}

if(!defined('BC_INCLUDED'))main();
