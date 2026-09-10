#!/usr/bin/env php
<?php
declare(strict_types=1);

const BTC_BASE = 'https://bitcotasks.com';
const SKIP_BASE = 'https://skipcha.online';
const CDATA = '268b60d486cdf66f02e16e4758f70a04456c106c67754bc3e12296cd3ac954a0';

$GLOBALS['UA']  = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36';
$GLOBALS['JAR'] = __DIR__ . '/cookies.txt';
$GLOBALS['KEY'] = null;
$GLOBALS['METHOD'] = 'bitcotasks_click';

function banner(): void {
    $w = 54;
    $bt = 'ðŸš€ BITCOTASKS BOT';
    $mt = 'Method: ' . $GLOBALS['METHOD'];
    echo "â•­" . str_repeat('â”€', $w) . "â•®" . PHP_EOL
        . 'â”‚ ' . $bt . str_repeat(' ', max(0, $w - 3 - mb_strlen($bt))) . 'â”‚' . PHP_EOL
        . 'â”œ' . str_repeat('â”€', $w) . 'â”¤' . PHP_EOL
        . 'â”‚ ' . $mt . str_repeat(' ', max(0, $w - 3 - mb_strlen($mt))) . 'â”‚' . PHP_EOL
        . "â•°" . str_repeat('â”€', $w) . "â•¯" . PHP_EOL . PHP_EOL;
}

function out(string $tag, string $msg): void {
    echo '[' . $tag . '] ' . $msg . PHP_EOL;
}

function find_api_key(): ?string {
    if (getenv('SKIPCHA_KEY')) return trim(getenv('SKIPCHA_KEY'));
    foreach ([__DIR__ . '/BASkey.txt', dirname(__DIR__) . '/BASkey.txt'] as $f) {
        if (is_file($f)) {
            $k = trim((string)file_get_contents($f));
            if ($k !== '') return $k;
        }
    }
    return null;
}

function http(string $url, string $method = 'GET', $data = null, array $extra = [], int $timeout = 40): array {
    $ch = curl_init($url);
    $headers = [
        'User-Agent: ' . $GLOBALS['UA'],
        'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8',
        'Sec-CH-UA: "Chromium";v="139", "Not;A=Brand";v="99"',
        'Sec-CH-UA-Mobile: ?1',
        'Sec-CH-UA-Platform: "Android"',
    ];
    foreach ($extra as $h) $headers[] = $h;
    $respHeaders = [];
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_HEADERFUNCTION => function ($ch, $h) use (&$respHeaders): int {
            $len = strlen($h);
            $t = trim($h);
            if ($t !== '' && strpos($t, ':') !== false) {
                [$name, $val] = explode(':', $t, 2);
                $respHeaders[strtolower($name)] = trim($val);
            }
            return $len;
        },
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEJAR => $GLOBALS['JAR'],
        CURLOPT_COOKIEFILE => $GLOBALS['JAR'],
        CURLOPT_ENCODING => 'gzip, deflate',
        CURLOPT_TIMEOUT => $timeout,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if (is_array($data)) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
        } else {
            curl_setopt($ch, CURLOPT_POSTFIELDS, (string)$data);
        }
    }
    $body = (string)curl_exec($ch);
    $status = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    $err = curl_error($ch);
    if ($err !== '') throw new RuntimeException('HTTP error: ' . $err . ' @ ' . $url);
    return ['status' => $status, 'body' => $body, 'headers' => $respHeaders];
}

function parse_js_str(string $html, string $name): ?string {
    $patterns = [
        '/(?:var|let|const)\s+' . preg_quote($name, '/') . '\s*=\s*["\']([^"\']*)["\']/s',
        '/' . preg_quote($name, '/') . '\s*:\s*["\']([^"\']*)["\']/s',
        '/"'.$name.'"\\s*:\\s*"([^"]*)"/s',
        '/\''.$name.'\'\\s*:\\s*\'([^\']*)\'/s',
    ];
    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $html, $m)) {
            return str_replace('\\/', '/', $m[1]);
        }
    }
    return null;
}

function ajax_headers(string $referer): array {
    return [
        'Accept: application/json, text/javascript, */*; q=0.01',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $referer,
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: cors',
        'Sec-Fetch-Dest: empty',
    ];
}

function ensure_fp_cookies(): void {
    $jar = $GLOBALS['JAR'];
    $fid = base64_encode(json_encode([
        'fid'     => bin2hex(random_bytes(16)),
        'fidnoua' => bin2hex(random_bytes(16)),
    ], JSON_UNESCAPED_SLASHES));
    $now = time();
    $cid = (string)mt_rand(1000000000, 9999999999);
    $cookies = [
        ['bitmedia_fid', $fid],
        ['_ga', 'GA1.1.' . $cid . '.' . $now],
        ['_ga_7LW1SRT2ZV', 'GS2.1.s' . $now . '$o1$g1$t' . $now . '$j100$l0$h0'],
    ];
    $lines = is_file($jar) ? file($jar, FILE_IGNORE_NEW_LINES) : [];
    $keep = [];
    foreach ($lines as $l) {
        if ($l === '' || $l[0] === '#') continue;
        $p = preg_split("/\t/", $l);
        if (count($p) >= 6 && in_array($p[5], ['bitmedia_fid', '_ga', '_ga_7LW1SRT2ZV'], true)) continue;
        $keep[] = $l;
    }
    $out = ["# Netscape HTTP Cookie File", "# https://curl.se/docs/http-cookies.html"];
    foreach ($keep as $l) $out[] = $l;
    foreach ($cookies as [$name, $val]) {
        $out[] = 'bitcotasks.com' . "\t" . 'FALSE' . "\t" . '/' . "\t" . 'FALSE' . "\t" . '0' . "\t" . $name . "\t" . $val;
    }
    file_put_contents($jar, implode(PHP_EOL, $out));
}

function parse_duration(string $html): int {
    if (preg_match('/var\s+duration\s*=\s*(\d+)\s*>=/', $html, $m)) {
        $d = (int)$m[1];
        return $d >= 30 ? $d - 1 : $d;
    }
    if (preg_match('/var\s+duration\s*=\s*(\d+);/', $html, $m)) return (int)$m[1];
    return 0;
}

function skipcha_post_image(string $b64): string {
    $params = ['key' => $GLOBALS['KEY'], 'method' => $GLOBALS['METHOD'], 'json' => 1];
    $url = SKIP_BASE . '/in.php?' . http_build_query($params);
    $r = http($url, 'POST', json_encode(['image' => $b64]), [
        'Content-Type: application/json',
        'Accept: application/json',
    ], 90);
    $j = json_decode($r['body'], true);
    if (!is_array($j)) throw new RuntimeException('skipcha /in.php bad response: ' . substr($r['body'], 0, 200));
    if (($j['status'] ?? 0) !== 1) {
        throw new RuntimeException('skipcha submit failed: ' . ($j['request'] ?? 'unknown'));
    }
    $id = (string)$j['request'];
    $deadline = microtime(true) + 90;
    while (microtime(true) < $deadline) {
        $r = http(SKIP_BASE . '/res.php?' . http_build_query([
            'key' => $GLOBALS['KEY'], 'action' => 'get', 'id' => $id, 'json' => 1,
        ]), 'GET', null, ['Accept: application/json'], 30);
        $j = json_decode($r['body'], true);
        if (!is_array($j)) throw new RuntimeException('skipcha /res.php bad response: ' . substr($r['body'], 0, 200));
        if (($j['status'] ?? 0) === 1) return (string)$j['request'];
        $msg = strtoupper((string)($j['request'] ?? ''));
        if ($msg !== '' && $msg !== 'CAPCHA_NOT_READY') throw new RuntimeException('skipcha failed: ' . $msg);
        usleep(2500000);
    }
    throw new RuntimeException('skipcha solve timeout');
}

function parse_coords(string $s): array {
    if (preg_match_all('/\d{1,4}/', $s, $m)) {
        $all = $m[0];
        if (count($all) >= 2) return [(int)$all[0], (int)$all[1]];
    }
    throw new RuntimeException('could not parse click coords from: ' . $s);
}

function fetch_captcha_challenge(string $bundleId, string $referer): array {
    $url = BTC_BASE . '/captcha2/' . $bundleId . '.js?action=captcha';
    $r = http($url, 'POST', json_encode(['t' => (int)(microtime(true) * 1000), 'r' => mt_rand(0, PHP_INT_MAX) / PHP_INT_MAX]), [
        'Content-Type: application/json',
        'Accept: application/json',
        'X-Requested-With: XMLHttpRequest',
        'Cache-Control: no-store',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $referer,
    ], 30);
    $j = json_decode($r['body'], true);
    if (!is_array($j)) throw new RuntimeException('captcha challenge is not JSON: ' . substr($r['body'], 0, 160));
    if (isset($j['error'])) throw new RuntimeException('captcha challenge error: ' . ($j['message'] ?? $j['error']));
    if (empty($j['image']) && !empty($j['preload'])) {
        $j['image'] = $j['preload'];
    }
    if (empty($j['image'])) throw new RuntimeException('captcha challenge missing image');
    return $j;
}

function parse_captcha_variant(string $js, string $target = ''): array {
    if (preg_match('/getElementById\("(\w+)"\)\.value\s*=\s*response\.(\w+)/', $js, $m)) {
        $inputId = $m[1];
        $tokenField = $m[2];
    } else {
        $needle = 'getElementById("' . $target . '").value = response.';
        $pos = strpos($js, $needle);
        if ($pos === false) throw new RuntimeException('captcha variant for input "' . $target . '" not found');
        $inputId = $target;
        $tokenField = '';
        for ($i = $pos + strlen($needle); $i < strlen($js); $i++) {
            $c = $js[$i];
            if (ctype_alnum($c)) $tokenField .= $c; else break;
        }
        if ($tokenField === '') throw new RuntimeException('captcha token field not found near "' . $target . '"');
    }
    $needle = 'getElementById("' . $inputId . '").value = response.';
    $pos = strpos($js, $needle);
    if ($pos === false) $pos = 0;
    $win = substr($js, max(0, $pos - 3500), 4600);

    $successField = null;
    if (preg_match_all('/if\s*\(response\.([A-Za-z0-9]+)\)/', $win, $ms)) {
        $successField = $ms[1][count($ms[1]) - 1];
    }
    if (!$successField) throw new RuntimeException('captcha success field not found');

    $dataUrl = null;
    if (preg_match('/xhr\.open\("POST", "([^"]+action=data[^"]+)"/', $win, $du)) {
        $dataUrl = strpos($du[1], 'http') === 0 ? $du[1] : BTC_BASE . $du[1];
    }
    if (!$dataUrl) throw new RuntimeException('captcha data url not found');

    $prefix = null; $coordField = null;
    if (preg_match('/var payload = "([A-Za-z0-9]+)=([^"&]+)&([A-Za-z0-9]+)="/', $win, $pp)) {
        $prefix = $pp[1] . '=' . $pp[2] . '&';
        $coordField = $pp[3];
    }
    if ($prefix === null) throw new RuntimeException('captcha payload fields not found');
    if (strpos($dataUrl, 'cdata=') === false) $dataUrl .= '&cdata=' . CDATA;

    return [
        'dataUrl'      => $dataUrl,
        'prefix'       => $prefix,
        'coordField'   => $coordField,
        'successField' => $successField,
        'tokenField'   => $tokenField,
    ];
}

function solve_captcha(string $referer, string $bundleId, string $target, int $attempts = 3, bool $quiet = false): string {
    $jsR = http(BTC_BASE . '/captcha2/' . $bundleId . '.js?action=captcha', 'GET', null, [
        'Accept: */*',
        'Referer: ' . $referer,
        'Cache-Control: no-cache',
    ], 40);
    $variant = parse_captcha_variant($jsR['body'], $target);

    for ($try = 1; $try <= $attempts; $try++) {
        if ($try > 1 && !$quiet) out('!', 'captcha rejected, retrying ' . $try . '/' . $attempts);
        if (!$quiet) out('-', 'solving captcha...');
        $challenge = fetch_captcha_challenge($bundleId, $referer);
        $started = microtime(true);
        $coordsRaw = skipcha_post_image($challenge['image']);
        [$x, $y] = parse_coords($coordsRaw);
        $w = max(1, (int)($challenge['w'] ?? 260));
        $h = max(1, (int)($challenge['h'] ?? 100));
        $x = min(max($x, 0), $w - 1);
        $y = min(max($y, 0), $h - 1);

        $elapsedMs = (int)((microtime(true) - $started) * 1000);
        if ($elapsedMs < 800) usleep((800 - $elapsedMs) * 1000);

        $body = $variant['prefix'] . $variant['coordField'] . '=' . urlencode('[' . $x . ',' . $y . ']');
        $r = http($variant['dataUrl'], 'POST', $body, [
            'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
            'Accept: application/json, text/javascript, */*; q=0.01',
            'X-Requested-With: XMLHttpRequest',
            'Origin: ' . BTC_BASE,
            'Referer: ' . $referer,
        ], 30);
        $j = json_decode($r['body'], true);
        if (!is_array($j)) throw new RuntimeException('captcha submit not JSON: ' . substr($r['body'], 0, 160));
        if (!empty($j[$variant['successField']])) {
            $token = (string)($j[$variant['tokenField']] ?? '');
            if ($token === '') throw new RuntimeException('captcha verified but token field empty');
            if (!$quiet) out('+', 'captcha solved');
            return $token;
        }
        if (!$quiet) out('!', 'captcha rejected: ' . (is_string($j['message'] ?? null) ? $j['message'] : 'no message'));
    }
    throw new RuntimeException('captcha could not be solved after ' . $attempts . ' attempts');
}

function fetch_guarded(string $url, int $depth = 0): array {
    if ($depth > 5) throw new RuntimeException('too many firewall loops');
    $r = http($url, 'GET', null, [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-Dest: document',
    ], 40);
    $b = $r['body'];
    $isGuard = (strpos($b, 'captchaTokenName') !== false)
        || (strpos($b, 'BitcoTasks â€” Verification') !== false)
        || strpos($url, 'firewall.php') !== false;
    if (!$isGuard) {
        if (strlen($b) < 1000
            && preg_match("/window\.location\.href\s*=\s*'([^']+)';/", $b, $rd)) {
            out('!', 'js gate -> ' . $rd[1]);
            return fetch_guarded($rd[1], $depth + 1);
        }
        return [$url, $b];
    }

    out('!', 'firewall page detected, solving guard captcha...');
    if (!preg_match('/captcha2\/([a-f0-9]+)\.js\?action=captcha/', $b, $m)) {
        throw new RuntimeException('firewall page has no captcha script');
    }
    $bundleId = $m[1];
    $capName = parse_js_str($b, 'captchaTokenName') ?? 'WXeq';
    out('*', 'firewall guard target: ' . $capName . ' bundle=' . substr($bundleId, 0, 12) . '...');
    $token = solve_captcha($url, $bundleId, $capName);
    $post = http($url, 'POST', [$capName => $token, 'action' => 'validate'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
    ], 40);
    $p = $post['body'];
    $target = null;
    if (preg_match("/window\.location\.href\s*=\s*'([^']+)'/", $p, $m)) $target = $m[1];
    elseif (($jj = json_decode($p, true)) && isset($jj['redirect'])) $target = $jj['redirect'];
    elseif (($hh = $post['headers']['location'] ?? null)) $target = $hh;
    if (!$target) throw new RuntimeException('firewall validate did not return a target: ' . substr($p, 0, 200));
    out('+', 'firewall passed -> ' . $target);
    return fetch_guarded($target, $depth + 1);
}

function complete_lead(string $leadUrl): bool {
    [$effUrl, $html] = fetch_guarded($leadUrl);
    $leadUrl = $effUrl;

    $hash      = parse_js_str($html, 'hash');
    $key       = parse_js_str($html, 'api_key');
    $token     = parse_js_str($html, 'token');
    $ctoken    = parse_js_str($html, 'ctoken');
    $sub_id    = parse_js_str($html, 'sub_id');
    $duration  = parse_duration($html);
    $iframeUrl = parse_js_str($html, 'iframeUrl');
    if (!$hash || !$key || !$token || !$ctoken || !$sub_id) {
        throw new RuntimeException('lead page missing expected variables');
    }
    if (!preg_match('/captcha2\/([a-f0-9]+)\.js\?action=captcha/', $html, $m)) {
        throw new RuntimeException('lead page has no captcha script');
    }
    $bundleId = $m[1];

    $capToken = solve_captcha($leadUrl, $bundleId, $ctoken);

    $sv = http($leadUrl, 'POST', ['action' => 'start_view'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: */*',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $leadUrl,
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: cors',
        'Sec-Fetch-Dest: empty',
    ], 30);

    $wait = max(5, $duration + 5);
    sleep($wait);

    $payload = [
        'hash'   => $hash,
        'sub_id' => $sub_id,
        'key'    => $key,
        'token'  => $token,
        'action' => 'proccessLead',
        $ctoken  => $capToken,
    ];
    $pl = http(BTC_BASE . '/system/ajax.php', 'POST', $payload, [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: application/json, text/javascript, */*; q=0.01',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $leadUrl,
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: cors',
        'Sec-Fetch-Dest: empty',
    ], 30);
    $j = json_decode($pl['body'], true);
    if (is_array($j)) {
        $status = $j['status'] ?? '?';
        $msg = trim(strip_tags((string)($j['message'] ?? '')));
        $redirect = $j['redirect'] ?? '';
        if ($status == 200) {
            out('+', $msg !== '' ? $msg : 'SUCCESS! This offer was successfully completed!');
            out('*', 'next: ' . $redirect);
            return true;
        }
        out('!', 'lead not credited: ' . $msg);
        return false;
    }
    out('!', 'unexpected proccessLead response: ' . substr($pl['body'], 0, 200));
    return false;
}

function wall_flow(string $wallUrl, ?int $index): void {
    out('-', 'loading offerwall: ' . $wallUrl);
    [$effUrl, $html] = fetch_guarded($wallUrl);
    $wallUrl = $effUrl;
    $tapToken = parse_js_str($html, 'token');
    $seg = explode('/', trim((string)parse_url($wallUrl, PHP_URL_PATH), '/'));
    $key = $seg[1] ?? null;
    $sid = $seg[2] ?? null;
    if (!$tapToken || !$key || !$sid) throw new RuntimeException('offerwall page missing token/key/sid');
    out('*', 'wall: key=' . $key . ' sid=' . $sid . ' tapToken=' . substr($tapToken, 0, 16) . '...');

    $postUrl = BTC_BASE . '/offerwall/' . $key . '/' . $sid . '/' . $seg[3];
    $r = http($postUrl, 'POST', ['token' => $tapToken, 'action' => 'switch_cat', 'type' => 'ptc'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: application/json, text/javascript, */*; q=0.01',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $wallUrl,
    ], 30);
    $j = json_decode($r['body'], true);
    if (!$j || !isset($j['items']) || !$j['items']) throw new RuntimeException('no PTC ads returned');
    $items = $j['items'];
    out('*', count($items) . ' PTC ads available');
    if ($index !== null) {
        $item = $items[$index] ?? null;
        if (!$item) throw new RuntimeException('index ' . $index . ' out of range');
    } else {
        $item = null;
        foreach ($items as $it) {
            if (($it['ad_type'] ?? '') === 'window' && (int)($it['duration'] ?? 99) <= 10) { $item = $it; break; }
        }
        if (!$item) $item = $items[0];
    }
    out('*', 'picked ad #' . $item['id'] . ' "' . $item['title'] . '" reward=' . $item['reward'] . ' ' . $item['reward_name'] . ' dur=' . $item['duration'] . 's');

    $r = http($postUrl, 'POST', [
        'token' => $tapToken, 'action' => 'init_transaction', 'hash' => $item['hash'],
        'sid' => $sid, 'key' => $key, 'type' => 'ptc',
    ], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: application/json, text/javascript, */*; q=0.01',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $wallUrl,
    ], 30);
    $j = json_decode($r['body'], true);
    if (!$j || empty($j['offer'])) throw new RuntimeException('init_transaction failed: ' . substr($r['body'], 0, 200));
    $lead = $j['offer'];
    out('+', 'ad opened -> ' . $lead);
    out('*', complete_lead($lead) ? 'PTC completed OK' : 'PTC completion FAILED');
}

function wall_loop(string $entry, ?int $index, int $budget = 0, int $maxLeads = 200): void {
    $deadline = $budget > 0 ? microtime(true) + $budget : 0;
    out('-', 'wall mode: loading ad list once, completing PTCs until none left'
        . ($deadline ? ' (budget ' . $budget . 's)' : ''));
    [$eff, $html] = fetch_guarded($entry);
    if (strpos($eff, '/lead/') !== false) {
        out('-', complete_lead($eff) ? 'lead completed' : 'lead failed');
        return;
    }
    $tapToken = parse_js_str($html, 'token');
    $seg = explode('/', trim((string)parse_url($eff, PHP_URL_PATH), '/'));
    $key = $seg[1] ?? null;
    $sid = $seg[2] ?? null;
    $urlToken = $seg[3] ?? $tapToken;
    if (!$tapToken || !$key || !$sid || !$urlToken) throw new RuntimeException('offerwall page missing token/key/sid');
    out('*', 'wall: key=' . $key . ' sid=' . $sid);
    $postBase = BTC_BASE . '/offerwall/' . $key . '/' . $sid . '/' . $urlToken;

    $r = http($postBase, 'POST', ['token' => $tapToken, 'action' => 'switch_cat', 'type' => 'ptc'],
        array_merge(['Content-Type: application/x-www-form-urlencoded; charset=UTF-8'], ajax_headers($wallUrl = $eff)), 30);
    $j = json_decode($r['body'], true);
    if (!$j || empty($j['items'])) throw new RuntimeException('no PTC ads returned: ' . substr($r['body'], 0, 160));
    $items = $j['items'];
    out('*', count($items) . ' PTC ads available');

    $order = [];
    foreach ($items as $i => $it) $order[] = $i;
    if ($index !== null && $index !== 0 && $index < count($items)) {
        $pref = [$index];
        foreach ($order as $i) if ($i !== $index) $pref[] = $i;
        $order = $pref;
    }
    $ok = 0;
    $skipped = [];
    $processed = 0;
    foreach ($order as $i) {
        if ($processed >= $maxLeads) break;
        if ($deadline && microtime(true) >= $deadline) { out('!', 'budget reached, stopping'); break; }
        $item = $items[$i];
        $processed++;
        out('+', 'ad: ' . $item['title']);
        try {
            $r = http($postBase, 'POST', [
                'token' => $tapToken, 'action' => 'init_transaction', 'hash' => $item['hash'],
                'sid' => $sid, 'key' => $key, 'type' => 'ptc',
            ], array_merge(['Content-Type: application/x-www-form-urlencoded; charset=UTF-8'], ajax_headers($wallUrl)), 30);
            $j = json_decode($r['body'], true);
            if (!$j || empty($j['offer'])) {
                out('!', 'init_transaction failed: ' . substr($r['body'], 0, 160));
                $skipped[] = $item['id'];
                continue;
            }
            $lead = $j['offer'];
            if (complete_lead($lead)) $ok++; else $skipped[] = $item['id'];
        } catch (Throwable $e) {
            out('!', 'error: ' . $e->getMessage());
            $skipped[] = $item['id'];
        }
    }
    out('+', 'done: ' . $ok . ' completed' . ($skipped ? ', skipped ' . count($skipped) : '') . ' of ' . count($items));
}

function readln(string $prompt): string {
    echo $prompt;
    $line = fgets(STDIN);
    return $line === false ? '' : trim($line);
}

function interactive_wizard(): void {
    banner();
    $keyFile = __DIR__ . '/BASkey.txt';
    $key = is_file($keyFile) ? trim((string)file_get_contents($keyFile)) : '';
    if ($key !== '') {
        out('*', 'using API key from ' . basename($keyFile)
            . ' (' . substr($key, 0, 6) . '...' . substr($key, -4) . ')');
    } else {
        out('!', 'no API key in ' . basename($keyFile));
        $key = trim(readln('SkipCha API key: '));
        if ($key === '') throw new RuntimeException('API key required');
        $r = http(SKIP_BASE . '/res.php?' . http_build_query(['key' => $key, 'action' => 'getbalance', 'json' => 1]));
        $bal = json_decode($r['body'], true);
        if (!isset($bal['balance'])) throw new RuntimeException('invalid API key: ' . substr($r['body'], 0, 120));
        file_put_contents($keyFile, $key . PHP_EOL);
        out('+', 'saved to ' . basename($keyFile));
        out('*', 'balance: ' . $bal['balance']);
    }
    $GLOBALS['KEY'] = $key;

    $url = trim(readln('Offerwall / firewall URL (https://bitcotasks.com/...): '));
    if ($url === '') throw new RuntimeException('offerwall URL required');
    if (strpos($url, 'bitcotasks.com') === false) {
        $url = BTC_BASE . ($url !== '' && $url[0] === '/' ? $url : '/' . $url);
    }

    $ua = trim(readln('User-Agent [default]: '));
    if ($ua !== '') $GLOBALS['UA'] = $ua;

    $method = trim(readln('Captcha method [' . $GLOBALS['METHOD'] . ']: '));
    if ($method !== '') $GLOBALS['METHOD'] = $method;

    out('*', 'method: ' . $GLOBALS['METHOD']);
    out('-', 'starting PTC completion (UA=' . substr($GLOBALS['UA'], 0, 30) . '...)...');
    wall_loop($url, null, 0);
}

function ui_cw(string $p, string $c, int $w): string {
    $s = mb_strlen($c);
    return $p . $c . str_repeat(' ', max(0, $w - mb_strlen($p) - $s)) . "â”‚\n";
}
function ui_tr(string $t, int $m): string {
    return mb_strlen($t) <= $m ? $t : mb_substr($t, 0, $m - 1) . "â€¦";
}
function ui_timer(int $s): void {
    for ($i = $s; $i >= 1; $i--) {
        echo "\r\033[K" . '  â”œâ”€ â³ ' . str_pad((string)$i, 2, ' ', STR_PAD_LEFT) . 's...';
        flush();
        if ($i > 1) sleep(1);
    }
    echo "\r\033[K" . '  â”œâ”€ Viewed âœ…' . PHP_EOL;
    flush();
}

function uj(string $base, string $rel): string {
    if (preg_match('#^[a-z][a-z0-9+.-]*://#i', $rel)) return $rel;
    $p = parse_url($base);
    $s = $p['scheme'] ?? 'https';
    $h = $p['host'] ?? '';
    $pt = isset($p['port']) ? ':' . $p['port'] : '';
    if ($rel !== '' && $rel[0] === '/') return "$s://$h$pt$rel";
    $d = str_replace('\\', '/', dirname($p['path'] ?? '/'));
    return "$s://$h$pt" . rtrim($d, '/') . "/$rel";
}

function eks(string $u): array {
    $p = parse_url($u);
    $k = $s = null;
    if (isset($p['query'])) {
        parse_str($p['query'], $q);
        $k = $q['key'] ?? null;
        $s = $q['sub_id'] ?? null;
    }
    if (!$k || !$s) {
        $pp = explode('/', trim($p['path'] ?? '', '/'));
        if ($pp[0] ?? '' === 'offerwall' && count($pp) >= 3) { $k = $pp[1]; $s = $pp[2]; }
        elseif ($pp[0] ?? '' === 'lead' && count($pp) >= 4) { $k = $pp[2]; $s = $pp[3]; }
    }
    return [$k, $s];
}

function old_firewall_bypass(string $ui): ?array {
    $h1 = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-Dest: document',
    ];
    $fu = null;
    if (strpos($ui, 'firewall.php') !== false) {
        $fu = $ui;
    } else {
        $b = http($ui, 'GET', null, $h1, 40)['body'];
        if (!preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/", $b, $m)) return null;
        $fu = uj($ui, $m[1]);
    }
    $fb = http($fu, 'GET', null, $h1, 40)['body'];
    if (!preg_match('/captcha2\/([a-f0-9]+)\.js\?action=captcha/', $fb, $m)) { echo "  â”œâ”€ âŒ No captcha JS\n"; return null; }
    $bundleId = $m[1];
    if (!preg_match('/captchaTokenName\s*=\s*"([^"]+)"/', $fb, $m)) { echo "  â”œâ”€ âŒ No ctn\n"; return null; }
    $ctn = $m[1];
    $tk = solve_captcha($fu, $bundleId, $ctn, 3, true);
    echo "  âœ… Solved\n";
    $vr = http($fu, 'POST', ['action' => 'validate', $ctn => $tk], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $fu,
    ], 40);
    $vv = json_decode($vr['body'], true);
    $ou = null;
    if ($vv && ($vv['status'] ?? '') === 'success' && !empty($vv['redirect'])) $ou = uj($ui, $vv['redirect']);
    if (!$ou && preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/", $vr['body'], $m2)) $ou = uj($ui, $m2[1]);
    if (!$ou) { echo "  â”œâ”€ âŒ No redirect\n"; return null; }
    $ob = http($ou, 'GET', null, $h1, 40)['body'];
    return [$ou, $ob];
}

function ui_pal(string $pg, string $url, int $n, int $t, string $ti, string $rw): int {
    $v = ['token' => null, 'hash' => null, 'sub_id' => null, 'key' => null];
    foreach (['token', 'hash', 'sub_id', 'key', 'api_key'] as $k) {
        $dk = $k === 'api_key' ? 'key' : $k;
        if ($v[$dk] ?? null) continue;
        $val = parse_js_str($pg, $k);
        if ($val !== null) $v[$dk] = $val;
    }
    if (!$v['token'] || !$v['hash'] || !$v['sub_id'] || !$v['key']) { echo "  â”œâ”€ âŒ Missing vars\n"; return -1; }
    $ct = parse_js_str($pg, 'ctoken');
    if (!$ct) { echo "  â”œâ”€ âŒ No ctn field\n"; return -1; }
    if (!preg_match('/captcha2\/([a-f0-9]+)\.js\?action=captcha/', $pg, $m)) { echo "  â”œâ”€ âŒ No captcha JS\n"; return -1; }
    try {
        $tk = solve_captcha($url, $m[1], $ct, 2, true);
    } catch (Throwable $e) { echo "  â”œâ”€ âŒ Captcha fail: " . $e->getMessage() . "\n"; return 0; }
    if (!$tk) { echo "  â”œâ”€ âŒ Captcha fail\n"; return 0; }
    http($url, 'POST', ['action' => 'start_view'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: */*',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $url,
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: cors',
        'Sec-Fetch-Dest: empty',
    ], 30);
    $dur = parse_duration($pg);
    $wait = $dur > 0 ? $dur + 5 : 5;
    echo "  â”œâ”€ â³ Waiting {$wait}s...\n";
    ui_timer($wait);
    $pl = http(BTC_BASE . '/system/ajax.php', 'POST', [
        'hash' => $v['hash'], 'sub_id' => $v['sub_id'], 'key' => $v['key'], 'token' => $v['token'],
        'action' => 'proccessLead', $ct => $tk,
    ], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Accept: application/json, text/javascript, */*; q=0.01',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $url,
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-Mode: cors',
        'Sec-Fetch-Dest: empty',
    ], 30);
    $r = json_decode($pl['body'], true);
    if (!$r) { echo "  â”œâ”€ âŒ Lead parse\n"; return 0; }
    if (($r['status'] ?? 0) == 200) { echo "  â”œâ”€ âœ… " . strip_tags($r['message'] ?? '+' . $rw) . "\n"; return 1; }
    $msg = strip_tags((string)($r['message'] ?? ''));
    $lower = strtolower($msg);
    if (strpos($lower, 'no longer available') !== false
        || strpos($lower, 'not available') !== false
        || strpos($lower, 'expired') !== false
        || strpos($lower, 'sold out') !== false
        || strpos($lower, 'already completed') !== false
        || strpos($lower, 'already viewed') !== false) {
        echo "  â”œâ”€ â­ï¸ " . substr($msg, 0, 100) . "\n";
        return -1;
    }
    echo "  â”œâ”€ âŒ " . substr($msg, 0, 100) . "\n";
    return 0;
}

function ui_ptc(string $tk, array $ad, string $bu, int $n = 1, int $t = 1): int {
    $w = 54;
    $ti = $ad['title'] ?? 'Unknown';
    $rw = $ad['reward'] ?? '0';
    echo "â•­" . str_repeat('â”€', $w) . "â•®\n";
    echo ui_cw("â”‚ ðŸš€ AD $n/$t", '', $w);
    echo "â”œ" . str_repeat('â”€', $w) . "â”¤\n";
    echo ui_cw("â”‚ ðŸ“Œ ", ui_tr($ti, $w - 4), $w);
    echo ui_cw("â”‚ ðŸ’° ", ui_tr($rw, $w - 4), $w);
    $ok = 0;
    for ($attempt = 0; $attempt < 3; $attempt++) {
        if ($attempt > 0) { echo ui_cw("â”‚  ", 'â–¶ Re-fetching view URL...', $w); sleep(random_int(2, 4)); }
        echo "\r\033[K";
        echo ui_cw("â”‚  ", 'â–¶ Init...', $w);
        $r = http($bu, 'POST', [
            'hash' => $ad['hash'], 'sid' => $ad['sid'] ?? '', 'key' => $ad['key'], 'type' => 'ptc',
            'token' => $tk, 'action' => 'init_transaction',
        ], [
            'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With: XMLHttpRequest',
            'Origin: ' . BTC_BASE,
            'Referer: ' . $bu,
        ], 30);
        $rs = json_decode($r['body'], true);
        if (!$rs || ($rs['status'] ?? 0) === 999 || !isset($rs['offer'])) continue;
        $au = $rs['offer'];
        echo "\r\033[K";
        echo ui_cw("â”‚ ", 'â–¶ Init âœ…', $w);
        echo ui_cw("â”‚  ", 'â–¶ Load...', $w);
        $pg = http($au, 'GET', null, [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site: same-origin',
            'Sec-Fetch-Mode: navigate',
            'Sec-Fetch-User: ?1',
            'Sec-Fetch-Dest: document',
            'Upgrade-Insecure-Requests: 1',
            'Referer: ' . $bu,
        ], 40)['body'];
        echo "\r\033[K";
        echo ui_cw("â”‚ ", 'â–¶ Load âœ…', $w);
        $res = ui_pal($pg, $au, $n, $t, $ti, $rw);
        if ($res === 1) { $ok = 1; break; }
        if ($res === -1) { $ok = -1; break; }
    }
    $s = $ok === 1 ? 'âœ… DONE' : ($ok === -1 ? 'â­ï¸ SKIP' : 'âŒ FAILED');
    echo ($ok === 1 ? "\r\033[K".ui_cw("â”‚ ", 'â–¶ Done âœ…', $w) : '')
        . ui_cw("â”‚ ", ui_tr($s, $w - 2), $w)
        . "â•°" . str_repeat('â”€', $w) . "â•¯\n\n";
    return $ok;
}

function ui_ploop(string $tk, array $as, string $bu, array $skip = []): array {
    $sc = 0;
    $fa = [];
    $skipped = [];
    $n = 0;
    foreach ($as as $i => $a) {
        if (in_array($a['hash'], $skip, true)) continue;
        $n++;
        if ($n > 1) {
            $dl = random_int(3, 5);
            echo "\n  â”œâ”€ â³ Waiting {$dl}s before next ad...\n";
            sleep($dl);
        }
        echo "\n--- Ad $n/" . count($as) . " ---\n";
        $res = ui_ptc($tk, $a, $bu, $n, count($as));
        if ($res === 1) $sc++;
        elseif ($res === -1) $skipped[] = $a['hash'];
        else $fa[] = $a;
    }
    return [$sc, $fa, $skipped];
}

function fetch_switch_cat(string $ou, string $ot): array {
    $sb = http($ou, 'POST', ['token' => $ot, 'action' => 'switch_cat', 'type' => 'ptc'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $ou,
    ], 30)['body'];
    $pt = json_decode($sb, true);
    return $pt['items'] ?? [];
}

function old_ui_main(): void {
    system(strncasecmp(PHP_OS, 'WIN', 3) === 0 ? 'cls' : 'clear');
    $w = 54;
    $bt = 'BITCOTASKS BOT';
    echo "â•­" . str_repeat('â”€', $w) . "â•®\n"
        . "â”‚ $bt" . str_repeat(' ', max(0, $w - 2 - mb_strlen($bt))) . "â”‚\n"
        . "â•°" . str_repeat('â”€', $w) . "â•¯\n\n";
    $keyFile = __DIR__ . '/BASkey.txt';
    if (is_file($keyFile) && trim((string)file_get_contents($keyFile)) !== '') {
        $GLOBALS['KEY'] = trim((string)file_get_contents($keyFile));
        echo "âœ… Key loaded\n";
    } else {
        echo "ðŸ”‘ Enter key: ";
        $key = trim((string)fgets(STDIN));
        if ($key === '') { echo "âŒ Exit\n"; return; }
        $GLOBALS['KEY'] = $key;
        file_put_contents($keyFile, $key . PHP_EOL);
        echo "âœ… Key saved\n";
    }
    $ui = trim((string)readln('Link: '));
    if ($ui === '') { echo "âŒ No link\n"; return; }
    if (strpos($ui, 'view/') !== false || strpos($ui, '/lead/') !== false) {
        echo "ðŸ“Œ Direct PTC\n";
        $h1 = [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Sec-Fetch-Site: same-origin', 'Sec-Fetch-Mode: navigate', 'Sec-Fetch-Dest: document',
        ];
        [$url, $pg] = [$ui, http($ui, 'GET', null, $h1, 40)['body']];
        if (preg_match("/window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]/", $pg, $mg)) {
            $url = uj($ui, $mg[1]);
            $pg = http($url, 'GET', null, $h1, 40)['body'];
        }
        $ti = 'PTC Ad';
        if (preg_match('/<title>([^<]+)<\/title>/i', $pg, $m)) $ti = trim($m[1]);
        ui_pal($pg, $url, 1, 1, $ti, '0');
        return;
    }
    $pd = parse_url($ui);
    $bd = ($pd['scheme'] ?? 'https') . '://' . ($pd['host'] ?? 'bitcotasks.com');
    [$bk, $si] = eks($ui);
    if (!$bk || !$si) { echo "âŒ No key/sub_id\n"; return; }
    echo "ðŸ“Œ Key:$bk Sub:$si\n\nðŸ›¡ï¸ Firewall\n";
    $ou = old_firewall_bypass($ui);
    if (!$ou) { echo "âŒ Firewall bypass failed\n"; return; }
    [$ou, $ob] = $ou;
    $ot = parse_js_str($ob, 'token');
    if (!$ot) { echo "âŒ No OW token\n"; return; }
    echo "\nðŸš€ PTC offers...\n";
    $sb = http($ou, 'POST', ['token' => $ot, 'action' => 'switch_cat', 'type' => 'ptc'], [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With: XMLHttpRequest',
        'Origin: ' . BTC_BASE,
        'Referer: ' . $ou,
    ], 30)['body'];
    $pt = json_decode($sb, true);
    if (!$pt) { echo "  â”œâ”€ âŒ JSON err\n"; return; }
    $as = $pt['items'] ?? [];
    if (!$as) { echo "  â”œâ”€ âŒ No ads\n"; return; }
    echo "âœ… " . count($as) . " ads found\n" . str_repeat('=', 54) . "\n";
    $totalDone = 0;
    $allSkipped = [];
    $round = 1;
    $fa = $as;
    while (!empty($fa)) {
        if ($round > 1) {
            echo "\nðŸ”„ Round $round: re-fetching ad list...\n";
            sleep(3);
            $as = fetch_switch_cat($ou, $ot);
            if (!$as) { echo "  â”œâ”€ âŒ No ads left\n"; break; }
            $newAds = [];
            foreach ($as as $a) {
                if (!in_array($a['hash'], $allSkipped, true)) $newAds[] = $a;
            }
            if (!$newAds) { echo "  â”œâ”€ âœ… No new ads available\n"; break; }
            echo "  â”œâ”€ " . count($newAds) . " new ads found\n";
            $fa = $newAds;
        }
        [$sc, $fa, $skipped] = ui_ploop($ot, $fa, $ou, $allSkipped);
        $totalDone += $sc;
        $allSkipped = array_merge($allSkipped, $skipped);
        $round++;
        if ($round > 10) { echo "\nâš ï¸ Max rounds reached\n"; break; }
    }
    $ss = "âœ… $totalDone completed";
    echo "\nâ•­" . str_repeat('â”€', $w) . "â•®\n"
        . "â”‚ $ss" . str_repeat(' ', max(0, $w - 2 - mb_strlen($ss))) . "â”‚\n"
        . "â•°" . str_repeat('â”€', $w) . "â•¯\n\n";
}

function usage(): void {
    echo 'Usage:' . PHP_EOL
        . '  php ptc.php                              interactive wizard (key + offerwall URL + UA)' . PHP_EOL
        . '  php ptc.php --balance' . PHP_EOL
        . '  php ptc.php https://bitcotasks.com/lead/<HASH>/<KEY>/<SUB_ID>/<TOKEN>' . PHP_EOL
        . '  php ptc.php https://bitcotasks.com/offerwall/<KEY>/<SUB_ID>/<TOKEN> [--index N]' . PHP_EOL
        . 'Loop:' . PHP_EOL
        . '  php ptc.php <firewall-or-offerwall-url> --loop SECONDS   complete PTCs until none left or budget expires' . PHP_EOL
        . 'Options:' . PHP_EOL
        . '  --key <SKIPCHA_API_KEY>   override API key (default: BASkey.txt or SKIPCHA_KEY env)' . PHP_EOL
        . '  --method <NAME>           SkipCha method (default: bitcotasks_click)' . PHP_EOL;
}

$args = $argv;
array_shift($args);
$GLOBALS['KEY'] = find_api_key();
$index = null;
$loop = null;
$positional = null;
foreach ($args as $i => $a) {
    if ($a === '--key') { $GLOBALS['KEY'] = trim((string)($args[$i + 1] ?? '')); $args[$i] = $args[$i + 1] = ''; }
    elseif ($a === '--index') { $index = (int)($args[$i + 1] ?? 0); $args[$i] = $args[$i + 1] = ''; }
    elseif ($a === '--loop') { $loop = (int)($args[$i + 1] ?? 120); if ($loop <= 0) $loop = 120; $args[$i] = $args[$i + 1] = ''; }
    elseif ($a === '--method') { $m = trim((string)($args[$i + 1] ?? '')); if ($m !== '') $GLOBALS['METHOD'] = $m; $args[$i] = $args[$i + 1] = ''; }
}
foreach ($args as $a) {
    if ($a !== '' && $a[0] !== '-') { $positional = $a; break; }
}

try {
    ensure_fp_cookies();
    if ($positional === null && !in_array('--balance', $argv, true)) {
        old_ui_main();
        exit(0);
    }
    if (!$GLOBALS['KEY']) { throw new RuntimeException('no SkipCha API key (set --key, SKIPCHA_KEY env, or BASkey.txt)'); }
    if ($positional === '--balance' || $positional === null && in_array('--balance', $argv, true)) {
        $r = http(SKIP_BASE . '/res.php?' . http_build_query(['key' => $GLOBALS['KEY'], 'action' => 'getbalance', 'json' => 1]));
        $j = json_decode($r['body'], true);
        echo 'balance: ' . json_encode($j) . PHP_EOL;
        exit(0);
    }
    if (!$positional) { usage(); exit(1); }
    if (strpos($positional, 'firewall.php') !== false || strpos($positional, '/offerwall/') !== false) {
        if ($loop !== null) {
            wall_loop($positional, $index, $loop, 200);
            exit(0);
        }
        [$eff] = fetch_guarded($positional);
        if (strpos($eff, '/lead/') !== false) {
            exit(complete_lead($eff) ? 0 : 1);
        }
        wall_flow($eff, $index);
    } elseif (strpos($positional, '/lead/') !== false) {
        $ok = complete_lead($positional);
        exit($ok ? 0 : 1);
    } else {
        usage(); exit(1);
    }
} catch (Throwable $e) {
    out('!', 'ERROR: ' . $e->getMessage());
    exit(1);
}
