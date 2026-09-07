<?php

error_reporting(E_ALL & ~E_DEPRECATED);

defined('API_URL') or define('API_URL', 'https://bypassallshortlinks.space/api.php');
defined('API_KEY_FILE') or define('API_KEY_FILE', 'BASkey.txt');
defined('API_TIMEOUT') or define('API_TIMEOUT', 300);
defined('CONNECTION_TIMEOUT') or define('CONNECTION_TIMEOUT', 30);
defined('READ_TIMEOUT') or define('READ_TIMEOUT', 30);

$API_KEY = null;
$curl = null;

function getCurl() {
    global $curl;
    if (!$curl) {
        $curl = curl_init();
        curl_setopt($curl, CURLOPT_COOKIEFILE, __DIR__ . '/cookies.txt');
        curl_setopt($curl, CURLOPT_COOKIEJAR, __DIR__ . '/cookies.txt');
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_HEADER, false);
        curl_setopt($curl, CURLOPT_CONNECTTIMEOUT, CONNECTION_TIMEOUT);
        curl_setopt($curl, CURLOPT_TIMEOUT, READ_TIMEOUT);
        curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($curl, CURLOPT_MAXREDIRS, 5);
        curl_setopt($curl, CURLOPT_ENCODING, '');
        curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    }
    return $curl;
}

function request($method, $url, $data = null, $extraHeaders = [], $referer = null, $json = false, $followRedirects = true) {
    $ch = getCurl();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, $followRedirects);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, strtoupper($method));

    $headers = [];
    if ($referer) $headers[] = 'Referer: ' . $referer;

    if (strtoupper($method) === 'POST') {
        if ($json && is_array($data)) {
            $body = json_encode($data);
            $headers[] = 'Content-Type: application/json';
        } elseif (is_array($data)) {
            $body = http_build_query($data);
            $headers[] = 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8';
        } else {
            $body = $data;
        }
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    } else {
        curl_setopt($ch, CURLOPT_POST, false);
        curl_setopt($ch, CURLOPT_POSTFIELDS, null);
    }

    foreach ($extraHeaders as $h) {
        $headers[] = $h;
    }
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    $retries = 2;
    $response = null;
    $error = null;
    for ($i = 0; $i < $retries; $i++) {
        $response = curl_exec($ch);
        if ($response !== false) {
            $error = null;
            break;
        }
        $error = curl_error($ch);
        if ($i < $retries - 1) usleep(500000);
    }

    $info = curl_getinfo($ch);
    return [$response, $error, $info];
}

function urljoin($base, $rel) {
    if (preg_match('#^[a-z][a-z0-9+.-]*://#i', $rel)) return $rel;
    $parts = parse_url($base);
    $scheme = $parts['scheme'] ?? 'https';
    $host = $parts['host'] ?? '';
    $port = isset($parts['port']) ? ':' . $parts['port'] : '';
    if (strpos($rel, '/') === 0) {
        return $scheme . '://' . $host . $port . $rel;
    }
    $path = isset($parts['path']) ? $parts['path'] : '/';
    $dir = dirname($path);
    if ($dir === '\\') $dir = '/';
    $dir = str_replace('\\', '/', $dir);
    return $scheme . '://' . $host . $port . rtrim($dir, '/') . '/' . $rel;
}

function displayBanner() {
    $width = 54;
    echo "╭" . str_repeat('─', $width) . "╮\n";
    echo "│ BITCOTASKS BOT (PTC)" . str_repeat(' ', $width - 20) . "│\n";
    echo "├" . str_repeat('─', $width) . "┤\n";
    echo "│ 📱 TG: https://t.me/bypassallshortlinks1" . str_repeat(' ', $width - 39) . "│\n";
    echo "│ 💻 Developer: Abdul Qayoom Boohar" . str_repeat(' ', $width - 33) . "│\n";
    echo "╰" . str_repeat('─', $width) . "╯\n\n";
}

function getApiKey() {
    global $API_KEY;
    $file = __DIR__ . '/' . API_KEY_FILE;
    if (file_exists($file)) {
        $content = trim(file_get_contents($file));
        if ($content) {
            $API_KEY = $content;
            echo "✅ API key loaded from " . API_KEY_FILE . "\n";
            return true;
        }
    }
    echo "\n🔑 API Key Required\n";
    echo "Get your free API key from: bypassallshortlinks.space\n";
    echo "Enter your API key: ";
    $API_KEY = trim(fgets(STDIN));
    if (!$API_KEY) {
        echo "❌ No API key provided. Exiting.\n";
        return false;
    }
    file_put_contents($file, $API_KEY);
    echo "✅ API key saved to " . API_KEY_FILE . "\n";
    return true;
}

function pngb64($p, $w, $h) {
    if (empty($p)) return '';
    $raw = base64_decode($p);
    if ($raw === false) return '';
    $img = imagecreatetruecolor($w, $h);
    if (!$img) return '';
    imagealphablending($img, false);
    imagesavealpha($img, true);
    $bytes = unpack('C*', $raw);
    if (!$bytes) { imagedestroy($img); return ''; }
    $bi = 1;
    $total = $w * $h;
    for ($i = 0; $i < $total; $i++) {
        $x = $i % $w;
        $y = (int)($i / $w);
        $r = $bytes[$bi++] ?? 0;
        $g = $bytes[$bi++] ?? 0;
        $b_val = $bytes[$bi++] ?? 0;
        $a = $bytes[$bi++] ?? 0;
        if ($w < 64 && $a < 100) {
            $color = imagecolorallocatealpha($img, 255, 255, 255, 127);
        } else {
            $gdAlpha = 127 - (int)(($a * 127) / 255);
            $color = imagecolorallocatealpha($img, $r, $g, $b_val, $gdAlpha);
        }
        imagesetpixel($img, $x, $y, $color);
    }
    ob_start();
    imagepng($img);
    $result = base64_encode(ob_get_clean());
    return $result;
}

function apiSolve($main, $options, $optDims, $quiet = false) {
    global $API_KEY;
    $mb = pngb64($main, 200, 100);
    $obs = [];
    foreach ($options as $idx => $opt) {
        $dim = isset($optDims[$idx]) ? $optDims[$idx] : [32, 32];
        $obs[] = pngb64($opt, $dim[0], $dim[1]);
    }
    $obs = array_pad($obs, 8, '');
    $payload = ['api_key' => $API_KEY, 'action' => 'bitcotasks', 'main' => $mb, 'options' => $obs];

    $ch = curl_init(API_URL);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => API_TIMEOUT,
        CURLOPT_CONNECTTIMEOUT => CONNECTION_TIMEOUT,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if ($response === false) {
        echo "  ├─ ⚠️ API timeout after " . API_TIMEOUT . "s\n";
        return [null, null];
    }
    $data = json_decode($response, true);
    if (!$data) return [null, null];

    if (!empty($data['success']) || ($data['status'] ?? '') === 'success') {
        if (isset($data['remaining_balance']) && !$quiet) {
            echo "  ├─ 💰 Api balance: {$data['remaining_balance']} tokens\n";
        }
        $winner = $data['winner'] ?? null;
        $target = $data['target'] ?? null;
        return $winner !== null ? [(string)$winner, $target] : [null, null];
    }
    $errorStatus = $data['status'] ?? 'error';
    $errorMsg = $data['error'] ?? 'Unknown error';
    if ($errorStatus === 'insufficient_balance') {
        echo "  ├─ ❌ Insufficient balance: $errorMsg\n";
    } else {
        echo "  ├─ ❌ API error: $errorMsg\n";
    }
    return [null, null];
}

function apiSolveClick($imageData, $quiet = false) {
    global $API_KEY;
    if (preg_match('#^data:image/[^;]+;base64,(.+)$#s', $imageData, $m)) {
        $imageData = $m[1];
    }
    $baseUrl = 'https://bypassallshortlinks.space';
    $submitPayload = ['key' => $API_KEY, 'method' => 'bitcotasks_click', 'image' => $imageData];
    $ch = curl_init($baseUrl . '/in.php');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $submitPayload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => CONNECTION_TIMEOUT,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    if ($response === false) {
        if (!$quiet) echo "  ├─ ⚠️ Click API submit failed\n";
        return [null, null];
    }

    $taskId = null;
    if (preg_match('/^OK\|(.+)$/s', trim($response), $m)) {
        $taskId = trim($m[1]);
    } else {
        $submitData = json_decode($response, true);
        if ($submitData && !empty($submitData['request'])) {
            $taskId = $submitData['request'];
        }
    }
    if (!$taskId) {
        if (!$quiet) echo "  ├─ ❌ Click API submit error: " . substr($response, 0, 200) . "\n";
        return [null, null];
    }

    for ($attempt = 0; $attempt < 40; $attempt++) {
        sleep(3);
        $pollUrl = $baseUrl . '/res.php?key=' . urlencode($API_KEY) . '&action=get&id=' . urlencode($taskId) . '&json=1';
        $pCh = curl_init($pollUrl);
        curl_setopt_array($pCh, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 15,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
        ]);
        $pollResp = curl_exec($pCh);
        curl_close($pCh);
        if ($pollResp === false) continue;
        $pollResp = trim($pollResp);
        if (preg_match('/^OK\|(.+)$/s', $pollResp, $m2)) {
            $click = trim($m2[1]);
            $parts = array_map('intval', explode(',', trim($click, '[] ')));
            if (count($parts) >= 2) return [$parts[0], $parts[1]];
            return [null, null];
        }
        $pollData = json_decode($pollResp, true);
        if (!$pollData) continue;
        if (isset($pollData['status']) && $pollData['status'] == 1) {
            $click = $pollData['request'] ?? null;
            if (isset($pollData['remaining_balance']) && !$quiet) {
                echo "  ├─ 💰 Api balance: {$pollData['remaining_balance']} tokens\n";
            }
            if (is_string($click)) {
                $click = trim($click, '[] ');
                $parts = array_map('intval', explode(',', $click));
                if (count($parts) >= 2) return [$parts[0], $parts[1]];
            } elseif (is_array($click) && count($click) >= 2) {
                return [(int)$click[0], (int)$click[1]];
            }
            return [null, null];
        }
        $req = $pollData['request'] ?? '';
        if (strpos($req, 'ERROR') !== false) {
            if (!$quiet) echo "  ├─ ❌ Click API error: $req\n";
            return [null, null];
        }
    }
    if (!$quiet) echo "  ├─ ⚠️ Click API poll timeout\n";
    return [null, null];
}

function solvePow($c, $d) {
    if (empty($c)) return null;
    $p = str_repeat('0', (int)$d);
    for ($n = 0; $n < 2000000; $n++) {
        $h = hash('sha256', $c . ':' . $n);
        if (strncmp($h, $p, strlen($p)) === 0) {
            return ['nonce' => $n, 'hash' => $h];
        }
    }
    return null;
}

function extractJsParams($js) {
    $fn1 = $fv = $fn2 = $succ = $tokf = $pe = $ve = null;

    if (preg_match('/var payload = "([^"]+)"/', $js, $m)) {
        $parts = explode('&', $m[1]);
        if (count($parts) >= 2) {
            $a1 = explode('=', $parts[0]);
            $a2 = explode('=', $parts[1]);
            $fn1 = $a1[0];
            $fv = $a1[1] ?? '';
            $fn2 = $a2[0];
        } else {
            return null;
        }
    } else {
        if (!preg_match('/var payload = "([^=]+)=([^&]+)&([^=]+)="/', $js, $m)) return null;
        $fn1 = $m[1]; $fv = $m[2]; $fn2 = $m[3];
    }

    if (!preg_match('/if\s*\(response\.([A-Za-z0-9]+)\)/', $js, $m)) return null;
    $succ = $m[1];
    if (!preg_match('/value\s*=\s*response\.([A-Za-z0-9]+)/', $js, $m)) return null;
    $tokf = $m[1];
    if (!preg_match('#fetch\("(/captcha2/[^"]+\.js\?[^"]+)"#', $js, $m)) return null;
    $pe = $m[1];
    if (!preg_match('/xhr\.open\("POST",\s*"(\/captcha2\/[^"]+)"/', $js, $m)) return null;
    $ve = $m[1];

    return [$fn1, $fv, $fn2, $succ, $tokf, $pe, $ve];
}

function notifedCookie() {
    $exp = (new DateTime("now", new DateTimeZone("GMT")))->modify("+30 minutes")->format("D, d M Y H:i:s") . " GMT";
    $rand = substr(md5($exp), 2, 9);
    return '_bitco_notifad=ad_value_' . $rand . '; _bitco_notifad_expire=expires=' . $exp;
}

function clearLine() {
    echo "\r\033[K";
}

function showAdBox($current, $total, $title, $reward, $isRetry = false) {
    $width = 54;
    $tag = $isRetry ? ' [RETRY]' : '';
    echo "╭" . str_repeat('─', $width) . "╮\n";
    echo "│ 🚀 AD $current/$total$tag" . str_repeat(' ', $width - strlen("🚀 AD $current/$total$tag")) . "│\n";
    echo "├" . str_repeat('─', $width) . "┤\n";
    $shortTitle = mb_strlen($title) > 40 ? mb_substr($title, 0, 40) : $title;
    echo "│ 📌 $shortTitle" . str_repeat(' ', $width - 4 - mb_strlen($shortTitle)) . "│\n";
    echo "│ 💰 $reward" . str_repeat(' ', $width - 4 - mb_strlen($reward)) . "│\n";
}

function updateAdStatus($text, $success = null) {
    $width = 54;
    if ($success === true) {
        clearLine();
        $display = strpos($text, 'Verifying') !== false ? ' ▶ Verifying... ✅' : " ▶ $text ✅";
        echo "│ $display" . str_repeat(' ', $width - mb_strlen($display)) . "│\n";
    } elseif ($success === false) {
        clearLine();
        $display = strpos($text, 'Verifying') !== false ? ' ▶ Verifying... ❌' : " ▶ $text ❌";
        echo "│ $display" . str_repeat(' ', $width - mb_strlen($display)) . "│\n";
    } else {
        echo "│  ▶ $text..." . str_repeat(' ', $width - 7 - mb_strlen($text)) . "│\n";
    }
}

function completeAdBox($success = true) {
    $width = 54;
    $status = $success ? '' : '❌ FAILED';
    echo "│ $status" . str_repeat(' ', $width - mb_strlen($status)) . "│\n";
    echo "╰" . str_repeat('─', $width) . "╯\n\n";
}

function showRetryBanner($count) {
    $width = 54;
    echo "\n╭" . str_repeat('─', $width) . "╮\n";
    echo "│ 🔄 RETRYING $count FAILED ADS" . str_repeat(' ', $width - mb_strlen("🔄 RETRYING $count FAILED ADS")) . "│\n";
    echo "╰" . str_repeat('─', $width) . "╯\n\n";
}

function showSummaryBox($successCount, $totalCount, $earned = 0, $failedAds = []) {
    $width = 54;
    echo "\n╭" . str_repeat('─', $width) . "╮\n";
    echo "│ 📊 FINAL SUMMARY" . str_repeat(' ', $width - 16) . "│\n";
    echo "├" . str_repeat('─', $width) . "┤\n";
    echo "│ ✅ Completed: $successCount/$totalCount" . str_repeat(' ', $width - mb_strlen("✅ Completed: $successCount/$totalCount")) . "│\n";
    $earnedStr = number_format($earned, 2);
    if (count($failedAds) > 0) {
        echo "│ ❌ Permanently Failed: " . count($failedAds) . str_repeat(' ', $width - mb_strlen("❌ Permanently Failed: " . count($failedAds))) . "│\n";
        echo "├" . str_repeat('─', $width) . "┤\n";
        echo "│ Failed Ads:" . str_repeat(' ', $width - 12) . "│\n";
        $count = 0;
        foreach ($failedAds as $ad) {
            if ($count >= 5) break;
            $count++;
            $shortTitle = mb_strlen($ad['title']) > 30 ? mb_substr($ad['title'], 0, 30) . '...' : $ad['title'];
            $line = "$count. $shortTitle - {$ad['reward']}";
            echo "│ $line" . str_repeat(' ', $width - mb_strlen($line) - 1) . "│\n";
        }
        if (count($failedAds) > 5) {
            $line = "... and " . (count($failedAds) - 5) . " more";
            echo "│ $line" . str_repeat(' ', $width - mb_strlen($line) - 1) . "│\n";
        }
    }
    echo "├" . str_repeat('─', $width) . "┤\n";
    echo "│ 📱 TG: t.me/bypassallshortlinks1" . str_repeat(' ', $width - 31) . "│\n";
    echo "╰" . str_repeat('─', $width) . "╯\n\n";
}

function startTimer($seconds) {
    for ($i = $seconds; $i >= 1; $i--) {
        echo "\r\033[K" . str_pad("  ├─ ⏳ Waiting " . str_pad($i, 2, ' ', STR_PAD_LEFT) . "s...", 55);
        flush();
        if ($i > 1) sleep(1);
    }
    echo "\r\033[K" . str_pad("  ├─ Viewed ✅", 55) . "\n";
    flush();
}

function sendStartView($url, $refererUrl) {
    [$body, $err, $info] = request('POST', $url, ['action' => 'start_view'], [
        'X-Requested-With: XMLHttpRequest',
        'Origin: https://bitcotasks.com',
        'User-Agent: ' . USER_AGENT,
    ], $refererUrl);
    return !$err;
}

function initPtcAd($adInfo, $token, $refererUrl) {
    updateAdStatus('Initializing');
    $data = [
        'hash' => $adInfo['hash'],
        'sid' => $adInfo['sid'] ?? '',
        'key' => $adInfo['key'],
        'type' => 'ptc',
        'token' => $token,
        'action' => 'init_transaction'
    ];
    [$body, $err, $info] = request('POST', $refererUrl, $data, [
        'X-Requested-With: XMLHttpRequest',
        'Origin: https://bitcotasks.com',
        'User-Agent: ' . USER_AGENT,
    ], $refererUrl);
    if ($err) {
        updateAdStatus('Initializing (Network error)', false);
        return null;
    }
    $result = json_decode($body, true);
    if (!$result) {
        updateAdStatus('Initializing (No response)', false);
        return null;
    }
    if (($result['status'] ?? 0) === 999) {
        updateAdStatus('Initializing (Blocked)', false);
        return null;
    }
    if (isset($result['offer'])) {
        updateAdStatus('Initializing', true);
        $offerUrl = $result['offer'];
        if (!preg_match('#^https?://#i', $offerUrl)) {
            $offerUrl = urljoin($refererUrl, $offerUrl);
        }
        return $offerUrl;
    }
    updateAdStatus('Initializing (No offer)', false);
    return null;
}

function visitPtcAd($url, $refererUrl) {
    updateAdStatus('Loading page');
    [$body, $err, $info] = request('GET', $url, null, [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8',
        'Upgrade-Insecure-Requests: 1',
        'User-Agent: ' . USER_AGENT,
    ], $refererUrl);
    if ($err) {
        updateAdStatus("Loading page (Network error)", false);
        return null;
    }
    updateAdStatus('Loading page', true);
    return $body;
}

function processAdFromLeadPage($adPage, $actualAdUrl, $adNum, $totalAds, $title, $reward, $quiet = false) {
    $token2 = null; $hash2 = null; $subId2 = null; $key2 = null;
    $varPat = '/(?:var|let|const)\s+%s\s*=\s*[\'"]([^\'"]+)[\'"]/';
    if (preg_match(sprintf($varPat, 'token'), $adPage, $m)) $token2 = $m[1];
    if (preg_match(sprintf($varPat, 'hash'), $adPage, $m)) $hash2 = $m[1];
    if (preg_match(sprintf($varPat, 'sub_id'), $adPage, $m)) $subId2 = $m[1];
    if (preg_match(sprintf($varPat, 'api_key'), $adPage, $m)) $key2 = $m[1];
    if (!$key2 && preg_match(sprintf($varPat, 'key'), $adPage, $m)) $key2 = $m[1];

    if (!$token2 && preg_match('/data-token\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) $token2 = $m[1];
    if (!$hash2 && preg_match('/data-hash\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) $hash2 = $m[1];
    if (!$subId2 && preg_match('/data-sub-id\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) $subId2 = $m[1];
    if (!$key2 && preg_match('/data-key\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) $key2 = $m[1];

    if (!$token2 && preg_match('/"token"\s*:\s*"([^"]+)"/', $adPage, $m)) $token2 = $m[1];
    if (!$hash2 && preg_match('/"hash"\s*:\s*"([^"]+)"/', $adPage, $m)) $hash2 = $m[1];
    if (!$subId2 && preg_match('/"sub_id"\s*:\s*"([^"]+)"/', $adPage, $m)) $subId2 = $m[1];
    if (!$key2 && preg_match('/"key"\s*:\s*"([^"]+)"/', $adPage, $m)) $key2 = $m[1];

    if (!$token2 || !$hash2 || !$subId2 || !$key2) {
        if (!$quiet) echo "  ├─ ❌ Could not extract page variables (token=" . ($token2 ?: 'null') . " hash=" . ($hash2 ?: 'null') . " sub_id=" . ($subId2 ?: 'null') . " key=" . ($key2 ?: 'null') . ")\n";
        return false;
    }

    $ctn = null;
    if (preg_match('/var\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) {
        $ctn = $m[1];
    }
    if (!$ctn && preg_match('/const\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) {
        $ctn = $m[1];
    }
    if (!$ctn && preg_match('/let\s+ctoken\s*=\s*[\'"]([^\'"]+)[\'"]/', $adPage, $m)) {
        $ctn = $m[1];
    }
    if (!$ctn && preg_match('/const\s+captchaTokenName\s*=\s*"([^"]+)"/', $adPage, $m)) {
        $val = $m[1];
        if (strpos($val, '+') === false && strpos($val, 'ctoken') === false) {
            $ctn = $val;
        }
    }
    if (!$ctn && preg_match('/var\s+captchaTokenName\s*=\s*"([^"]+)"/', $adPage, $m)) {
        $val = $m[1];
        if (strpos($val, '+') === false && strpos($val, 'ctoken') === false) {
            $ctn = $val;
        }
    }
    if (!$ctn && preg_match('#var\s+captchaID\s*=\s*\$\(\'input\[name="([^"]+)"\]\'\)\.val\(\)#', $adPage, $m)) {
        $ctn = $m[1];
    }
    if (!$ctn) {
        if (preg_match_all('/<input[^>]+type\s*=\s*["\']hidden["\'][^>]*name\s*=\s*["\']([^"\']+)["\']/i', $adPage, $matches)) {
            foreach ($matches[1] as $hn) {
                if (stripos($hn, 'captcha') !== false || stripos($hn, 'token') !== false || stripos($hn, 'ctn') !== false || stripos($hn, 'recaptcha') !== false) {
                    $ctn = $hn;
                    break;
                }
            }
            if (!$ctn && !empty($matches[1])) $ctn = end($matches[1]);
        }
    }
    if (!$ctn && preg_match('/<input[^>]*name\s*=\s*"([^"]+)"[^>]*>/i', $adPage, $m)) {
        $ctn = $m[1];
    }
    if (!$ctn) {
        if (!$quiet) echo "  ├─ ❌ Could not find captcha input field\n";
        return false;
    }

    if (preg_match('/var (?:duration|timer)\s*=\s*(\d+);/', $adPage, $m)) {
        $duration = (int)$m[1];
        sendStartView($actualAdUrl, $actualAdUrl);
        startTimer($duration);
    } elseif (!$quiet) {
        echo str_pad("  ├─ Viewed ✅", 55) . "\n";
    }

    if (!preg_match('/src="(\/captcha2\/[^"]+\.js\?[^"]+)"/', $adPage, $m)) {
        if (!$quiet) echo "  ├─ ❌ No captcha JS found in page\n";
        return false;
    }
    $cjs = $m[1];
    $cjsu = urljoin($actualAdUrl, $cjs);
    $h = ['User-Agent: ' . USER_AGENT];
    [$jsBody, $err] = request('GET', $cjsu, null, $h, $actualAdUrl);
    if ($err) {
        if (!$quiet) echo "  ├─ ❌ Failed to load captcha JS: $err\n";
        return false;
    }

    $params = extractJsParams($jsBody);
    if (!$params) {
        if (!$quiet) echo "  ├─ ❌ Failed to extract captcha parameters\n";
        return false;
    }
    [$fn1, $fv, $fn2, $succ, $tokf, $pe, $ve] = $params;

    $pu = urljoin($actualAdUrl, $pe);
    [$capData, $err] = request('POST', $pu, ['t' => (int)(microtime(true) * 1000), 'r' => mt_rand() / mt_getrandmax()],
        array_merge($h, ['Content-Type: application/json']), $actualAdUrl, true);
    if ($err) {
        if (!$quiet) echo "  ├─ ❌ Failed to get captcha data: $err\n";
        return false;
    }
    $d = json_decode($capData, true);
    if (!$d) {
        if (!$quiet) echo "  ├─ ❌ Failed to parse captcha data\n";
        return false;
    }

    $clickMode = !empty($d['image']) && empty($d['options']);
    if ($clickMode) {
        [$cx, $cy] = apiSolveClick($d['image'], $quiet);
        if ($cx === null) {
            if (!$quiet) echo "  ├─ ❌ Captcha solve failed\n";
            return false;
        }
        $clickCoords = [$cx, $cy];
    } else {
        $opx = [];
        foreach ($d['options'] ?? [] as $o) $opx[] = $o['pixels'] ?? '';
        $odm = [];
        foreach ($d['options'] ?? [] as $o) $odm[] = [$o['width'] ?? 32, $o['height'] ?? 32];

        [$sel] = apiSolve($d['pixel'] ?? '', $opx, $odm, $quiet);
        if ($sel === null) {
            if (!$quiet) echo "  ├─ ❌ Captcha solve failed\n";
            return false;
        }
    }

    $powData = !empty($d['challenge']) ? solvePow($d['challenge'], $d['difficulty'] ?? 4) : null;
    $el = rand(3000, 8000);
    $mv = rand(5, 15);
    $cf = rand(300, 500);
    $nonce = $powData['nonce'] ?? 0;
    $challengeVal = $d['challenge'] ?? '';
    $br = "$el:{$nonce}:{$challengeVal}";
    $bh = hash('sha256', $br);

    $vp = [];
    $vp[$fn1] = $fv;
    $vp[$fn2] = json_encode($clickMode ? $clickCoords : [(int)$sel]);
    $vp['_et'] = (string)$el;
    $vp['_mv'] = (string)$mv;
    $vp['_cf'] = (string)$cf;
    $vp['_pw'] = $powData ? json_encode($powData) : 'null';
    $vp['_ch'] = $challengeVal;
    $vp['_bh'] = $bh;

    $vu = urljoin($actualAdUrl, $ve);
    $vdParts = [];
    foreach ($vp as $k => $v) $vdParts[] = urlencode($k) . '=' . urlencode($v);
    $vd = implode('&', $vdParts);

    [$valBody, $err] = request('POST', $vu, $vd, array_merge($h, ['Content-Type: application/x-www-form-urlencoded']), $actualAdUrl);
    if ($err) {
        if (!$quiet) echo "  ├─ ❌ Captcha validation failed: $err\n";
        return false;
    }
    $resp = json_decode($valBody, true);
    if (!$resp) {
        if (!$quiet) echo "  ├─ ❌ Failed to parse validation response\n";
        if (!$quiet) echo "  ├─ Raw: " . substr($valBody, 0, 200) . "\n";
        return false;
    }

    $validationSuccess = false;
    if (!empty($resp[$succ])) {
        $validationSuccess = true;
    } else {
        foreach ($resp as $k => $v) {
            if ($v === true) {
                $succ = $k;
                $validationSuccess = true;
                break;
            }
        }
    }
    if (!$validationSuccess) {
        if (!$quiet) echo "  ├─ ❌ Captcha validation returned failure: " . json_encode($resp) . "\n";
        return false;
    }

    $captchaToken = $resp[$tokf] ?? null;
    if (!$captchaToken) {
        foreach ($resp as $k => $v) {
            if (is_string($v) && preg_match('/^[a-f0-9]{32,}$/i', $v)) {
                $captchaToken = $v;
                break;
            }
        }
    }
    if (!$captchaToken) {
        if (!$quiet) echo "  ├─ ❌ Could not extract captcha token from validation response\n";
        if (!$quiet) echo "  ├─ Response: " . json_encode($resp) . "\n";
        return false;
    }

    $ajaxData = [
        'hash' => $hash2,
        'sub_id' => $subId2,
        'key' => $key2,
        'token' => $token2,
        $ctn => $captchaToken,
        'action' => 'proccessLead'
    ];

    if (!$quiet) echo "  ├─ 🔍 Submitting lead (ctn=$ctn, token_len=" . strlen($captchaToken) . ")\n";
    [$leadBody, $err] = request('POST', 'https://bitcotasks.com/system/ajax.php', $ajaxData, array_merge($h, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: https://bitcotasks.com',
    ]), $actualAdUrl);
    if ($err) {
        if (!$quiet) echo "  ├─ ❌ Failed to submit lead: $err\n";
        return false;
    }
    $result = json_decode($leadBody, true);
    if (!$result) {
        if (!$quiet) echo "  ├─ ❌ Failed to parse lead response\n";
        if ($leadBody && !$quiet) echo "  ├─ Response: " . substr($leadBody, 0, 200) . "\n";
        return false;
    }

    if (($result['status'] ?? 0) === 200) {
        $msg = strip_tags($result['message'] ?? "COMPLETED! +$reward");
        echo ($quiet ? "  ├─ ✅ $msg\n" : "  ├─ ✅ $msg\n");
        return true;
    }
    $errMsg = strip_tags($result['message'] ?? 'Unknown error');
    $errStatus = $result['status'] ?? 'unknown';
    echo "  ├─ ❌ Failed (status=$errStatus): " . substr($errMsg, 0, 150) . "\n";
    return false;
}

function processPtcAd($token, $ad, $baseUrl, $adNum = 1, $totalAds = 1) {
    $hid = $ad['hash'];
    $aid = $ad['id'];
    $sid = $ad['sid'] ?? '';
    $key = $ad['key'];
    $title = $ad['title'];
    $reward = $ad['reward'] ?? '0';

    showAdBox($adNum, $totalAds, $title, $reward);

    $actualAdUrl = initPtcAd($ad, $token, $baseUrl);
    if (!$actualAdUrl) {
        completeAdBox(false);
        return false;
    }

    $adPage = visitPtcAd($actualAdUrl, $baseUrl);
    if (!$adPage) {
        completeAdBox(false);
        return false;
    }

    $success = processAdFromLeadPage($adPage, $actualAdUrl, $adNum, $totalAds, $title, $reward);
    completeAdBox($success);
    return $success;
}

function processDirectPtcLink($viewUrl) {
    $headers = [
        'User-Agent: ' . USER_AGENT,
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8'
    ];

    [$viewBody, $err] = request('GET', $viewUrl, null, $headers, null, false, false);
    if ($err) {
        echo "  ├─ ❌ Failed to load view page: $err\n";
        return false;
    }

    $leadUrl = null;
    if (preg_match("/window\.location\.href\s*=\s*'([^']+)'/", $viewBody, $m)) {
        $leadUrl = $m[1];
    } elseif (preg_match('/window\.location\.href\s*=\s*"([^"]+)"/', $viewBody, $m)) {
        $leadUrl = $m[1];
    }
    if (!$leadUrl) {
        echo "  ├─ ❌ No redirect found in view page\n";
        return false;
    }
    $leadUrl = urljoin($viewUrl, $leadUrl);

    [$leadPage, $err] = request('GET', $leadUrl, null, $headers, $viewUrl);
    if ($err) {
        echo "  ├─ ❌ Failed to load lead page: $err\n";
        return false;
    }

    $title = 'Direct PTC Ad';
    if (preg_match('/<title>([^<]+)<\/title>/i', $leadPage, $m)) {
        $title = trim($m[1]);
    }

    echo "  📌 $title\n";
    $success = processAdFromLeadPage($leadPage, $leadUrl, 1, 1, $title, '0', false);
    return $success;
}

function processAdsLoop($token, $ads, $baseUrl, $isRetry = false) {
    $successCount = 0;
    $totalEarned = 0.0;
    $failedAds = [];

    foreach ($ads as $i => $ad) {
        $num = $i + 1;
        echo "\n--- Ad $num/" . count($ads) . " ---\n";
        if (processPtcAd($token, $ad, $baseUrl, $num, count($ads))) {
            $successCount++;
            $rewardStr = preg_replace('/[^\d.]/', '', explode(' ', $ad['reward'] ?? '0')[0]);
            $totalEarned += (float)$rewardStr;
        } else {
            $failedAds[] = $ad;
        }
        if ($i < count($ads) - 1) {
            sleep(rand(3, 5));
        }
    }
    return [$successCount, $totalEarned, $failedAds];
}

function extractKeySubidFromUrl($url) {
    $parts = parse_url($url);
    $key = null;
    $subId = null;
    if (isset($parts['query'])) {
        parse_str($parts['query'], $query);
        $key = $query['key'] ?? null;
        $subId = $query['sub_id'] ?? null;
    }
    if (!$key || !$subId) {
        $pathParts = explode('/', trim($parts['path'] ?? '', '/'));
        if (count($pathParts) >= 3 && $pathParts[0] === 'offerwall') {
            $key = $pathParts[1];
            $subId = $pathParts[2];
        }
    }
    return [$key, $subId];
}

function main() {
    global $argv;
    $argc = isset($argv) ? count($argv) : 0;

    $interactive = !($argc > 1 && !empty($argv[1]));

    if ($interactive) {
        system(strncasecmp(PHP_OS, 'WIN', 3) === 0 ? 'cls' : 'clear');
        displayBanner();
    }
    if (!getApiKey()) return;

    define('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36');

    if (!$interactive) {
        $userInput = trim($argv[1]);
    } else {
        echo "\n📋 Enter offerwall / firewall / PTC view link:\n";
        echo "╰─▶ ";
        $userInput = trim(fgets(STDIN));
    }
    if (!$userInput) {
        echo "❌ No link provided. Exiting.\n";
        return;
    }

    $userInput = trim($userInput);

    // Direct PTC view link — skip offerwall/firewall entirely
    if (strpos($userInput, '/view/') !== false) {
        echo "\n   📌 Direct PTC link detected\n";
        processDirectPtcLink($userInput);
        return;
    }

    $parsedUrl = parse_url($userInput);
    $baseDomain = $parsedUrl['scheme'] . '://' . $parsedUrl['host'];

    [$baseKey, $subId] = extractKeySubidFromUrl($userInput);

    if (!$baseKey || !$subId) {
        echo "❌ Could not extract key and sub_id from URL\n";
        echo "   Supported formats:\n";
        echo "   • https://bitcotasks.com/offerwall/KEY/SUB_ID\n";
        echo "   • https://bitcotasks.com/offerwall/KEY/SUB_ID/HASH\n";
        echo "   • https://bitcotasks.com/firewall.php?key=KEY&sub_id=SUB_ID\n";
        echo "   • https://bitcotasks.com/view/HASH:ENCRYPTED (direct PTC link)\n";
        return;
    }

    echo " │ 📌 Base Key: $baseKey, Sub ID: $subId\n";

    echo "\n🛡️ Firewall Bypass\n";

    $headers1 = [
        'User-Agent: ' . USER_AGENT,
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8'
    ];

    if (strpos($userInput, 'firewall.php') !== false) {
        $firewallPostUrl = $userInput;
        $fu = $userInput;
        [$firewallBody, $err] = request('GET', $firewallPostUrl, null, $headers1);
        if ($err) { echo "❌ Failed to load firewall page: $err\n"; return; }
        $firewallText = $firewallBody;

        if (!preg_match('/src="(\/captcha2\/[^"]+\.js\?action=captcha)"/', $firewallText, $m)) {
            echo "❌ Captcha JS not found\n";
            return;
        }
        $cjs = urljoin($baseDomain, $m[1]);
        $r2Text = $firewallText;
    } else {
        [$r1Body, $err] = request('GET', $userInput, null, $headers1, null, false, false);
        if ($err) { echo "❌ Failed to load offerwall: $err\n"; return; }

        if (!preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/", $r1Body, $m)) {
            echo "❌ No redirect found\n";
            return;
        }
        $loc = $m[1];

        [$r2Body, $err] = request('GET', $loc, null, $headers1, $userInput);
        if ($err) { echo "❌ Failed to follow redirect: $err\n"; return; }
        $r2Text = $r2Body;

        if (!preg_match('/src="(\/captcha2\/[^"]+\.js\?action=captcha)"/', $r2Text, $m)) {
            echo "❌ Captcha JS not found\n";
            return;
        }
        $cjs = urljoin($baseDomain, $m[1]);
        $fu = $loc;
        $firewallPostUrl = $baseDomain . '/firewall.php?key=' . $baseKey . '&sub_id=' . $subId;
    }

    if (!preg_match('/const\s+captchaTokenName\s*=\s*"([^"]+)"/', $r2Text, $m)) {
        echo "❌ Could not find captcha token name\n";
        return;
    }
    $ctn = $m[1];

    [$jsBody, $err] = request('GET', $cjs, null, $headers1, $fu);
    if ($err) { echo "❌ Failed to load captcha JS: $err\n"; return; }

    $initParams = extractJsParams($jsBody);
    if (!$initParams) { echo "❌ Failed to extract initial captcha parameters\n"; return; }
    [$fn1, $fv, $fn2, $succ, $tokf, $pe, $ve] = $initParams;

    $pu = urljoin($baseDomain, $pe);
    [$capData, $err] = request('POST', $pu,
        ['t' => (int)(microtime(true) * 1000), 'r' => mt_rand() / mt_getrandmax()],
        array_merge($headers1, ['Content-Type: application/json']), $fu, true);
    if ($err) { echo "❌ Failed to get captcha data: $err\n"; return; }
    $d = json_decode($capData, true);
    if (!$d) { echo "❌ Failed to parse captcha data\n"; return; }

    $clickMode = !empty($d['image']) && empty($d['options']);
    if ($clickMode) {
        [$cx, $cy] = apiSolveClick($d['image']);
        if ($cx === null) { echo "❌ Captcha solve failed\n"; return; }
        $clickCoords = [$cx, $cy];
        echo "   Captcha solved (click) ✅\n";
    } else {
        $opx = [];
        foreach ($d['options'] ?? [] as $o) $opx[] = $o['pixels'] ?? '';
        $odm = [];
        foreach ($d['options'] ?? [] as $o) $odm[] = [$o['width'] ?? 32, $o['height'] ?? 32];

        [$sel] = apiSolve($d['pixel'] ?? '', $opx, $odm);
        if ($sel === null) { echo "❌ Captcha solve failed\n"; return; }
        echo "   Captcha solved ✅\n";
    }

    $hasChallenge = !empty($d['challenge']);
    $powData = $hasChallenge ? solvePow($d['challenge'], $d['difficulty'] ?? 4) : null;
    $el = rand(3000, 8000);
    $mv = rand(5, 15);
    $cf = rand(300, 500);
    $challengeVal = $d['challenge'] ?? '';
    $nonce = $powData['nonce'] ?? 0;
    $br = "$el:{$nonce}:{$challengeVal}";
    $bh = hash('sha256', $br);

    $vp = [];
    $vp[$fn1] = $fv;
    $vp[$fn2] = json_encode($clickMode ? $clickCoords : [(int)$sel]);
    $vp['_et'] = (string)$el;
    $vp['_mv'] = (string)$mv;
    $vp['_cf'] = (string)$cf;
    $vp['_pw'] = $powData ? json_encode($powData) : 'null';
    $vp['_ch'] = $challengeVal;
    $vp['_bh'] = $bh;

    $vu = urljoin($baseDomain, $ve);
    $vdParts = [];
    foreach ($vp as $k => $v) $vdParts[] = urlencode($k) . '=' . urlencode($v);
    $vd = implode('&', $vdParts);

    [$valBody, $err] = request('POST', $vu, $vd,
        array_merge($headers1, ['Content-Type: application/x-www-form-urlencoded']), $fu);
    if ($err) { echo "❌ Validation failed: $err\n"; return; }
    $resp = json_decode($valBody, true);
    if (!$resp) { echo "❌ Failed to parse validation response\n"; return; }

    if (empty($resp[$succ])) {
        echo "❌ Validation failed\n";
        echo "   Response: " . json_encode($resp) . "\n";
        return;
    }
    $t = $resp[$tokf] ?? null;
    if (!$t) { echo "❌ Could not extract token\n"; return; }

    $validateData = ['action' => 'validate', $ctn => $t];
    [$valResp, $err] = request('POST', $fu, $validateData, $headers1);
    if ($err) { echo "❌ Token validation failed: $err\n"; return; }

    $offerwallUrl = null;
    $valJson = json_decode($valResp, true);
    if ($valJson && ($valJson['status'] ?? '') === 'success' && !empty($valJson['redirect'])) {
        $offerwallUrl = urljoin($baseDomain, $valJson['redirect']);
        echo "   Redirect found (JSON): " . substr($offerwallUrl, 0, 80) . "...\n";
    }
    if (!$offerwallUrl) {
        if (preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/", $valResp, $m)) {
            $offerwallUrl = urljoin($baseDomain, $m[1]);
            echo "   Redirect found (HTML): " . substr($offerwallUrl, 0, 80) . "...\n";
        }
    }
    if (!$offerwallUrl) {
        echo "❌ No redirect after validation\n";
        echo "   Response preview: " . substr($valResp, 0, 200) . "\n";
        return;
    }

    [$owBody, $err] = request('GET', $offerwallUrl, null, $headers1);
    if ($err) { echo "❌ Failed to load offerwall: $err\n"; return; }

    $offerwallToken = null;
    if (preg_match("/var\s+token\s*=\s*'([^']+)'/", $owBody, $m)) {
        $offerwallToken = $m[1];
    }
    if (!$offerwallToken) { echo "❌ Could not extract offerwall token\n"; return; }

    echo "\n🚀 Loading PTC offers...\n";
    $switchHeaders = array_merge($headers1, [
        'Authority: bitcotasks.com',
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: https://bitcotasks.com',
        'X-Requested-With: XMLHttpRequest'
    ]);
    $switchData = ['token' => $offerwallToken, 'action' => 'switch_cat', 'type' => 'ptc'];

    [$switchBody, $err] = request('POST', $offerwallUrl, $switchData, $switchHeaders, $offerwallUrl);
    if ($err) { echo "❌ Switch failed: $err\n"; return; }

    $ptcData = json_decode($switchBody, true);
    if (!$ptcData) { echo "❌ Invalid JSON response from switch\n"; return; }

    $ads = $ptcData['items'] ?? [];
    echo "✅ Found " . count($ads) . " PTC ads\n";

    echo "\n" . str_repeat('=', 60) . "\n";
    echo "PROCESSING PTC ADS\n";
    echo str_repeat('=', 60) . "\n";

    [$successCount, $totalEarned, $failedAds] = processAdsLoop($offerwallToken, $ads, $offerwallUrl);

    if (count($failedAds) > 0) {
        showRetryBanner(count($failedAds));
        sleep(2);
        [$retrySuccess, $retryEarned, $stillFailed] = processAdsLoop($offerwallToken, $failedAds, $offerwallUrl, true);
        $successCount += $retrySuccess;
        $totalEarned += $retryEarned;
        $failedAds = $stillFailed;
    }

    showSummaryBox($successCount, count($ads), $totalEarned, $failedAds);
}

if (!defined('BC_INCLUDED')) {
    main();
}
