import json
import os
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from accounts.models import CharacterProgress, StudySession, UserProfile, Achievement

# ── Load kanji ────────────────────────────────────────────────────────────────
_kanji_path = os.path.join(os.path.dirname(__file__), 'data', 'kanji.json')
with open(_kanji_path, 'r', encoding='utf-8') as f:
    KANJI = json.load(f)

# ── Achievements ──────────────────────────────────────────────────────────────
ACHIEVEMENTS = {
    'first_session':   {'icon': '🎌', 'title': 'First Steps',     'desc': 'Complete your first study session'},
    'streak_3':        {'icon': '🔥', 'title': 'On Fire',          'desc': 'Achieve a 3-day streak'},
    'streak_7':        {'icon': '🌟', 'title': 'Week Warrior',     'desc': 'Achieve a 7-day streak'},
    'streak_30':       {'icon': '👑', 'title': 'Unstoppable',      'desc': 'Achieve a 30-day streak'},
    'xp_100':          {'icon': '⚡', 'title': 'XP Hunter',        'desc': 'Earn 100 XP'},
    'xp_500':          {'icon': '💎', 'title': 'XP Master',        'desc': 'Earn 500 XP'},
    'xp_1000':         {'icon': '🏆', 'title': 'XP Legend',        'desc': 'Earn 1000 XP'},
    'hiragana_done':   {'icon': 'あ', 'title': 'Hiragana Hero',    'desc': 'Master all 46 hiragana'},
    'katakana_done':   {'icon': 'ア', 'title': 'Katakana King',    'desc': 'Master all 46 katakana'},
    'kanji_50':        {'icon': '漢', 'title': 'Kanji Beginner',   'desc': 'Master 50 kanji'},
    'perfect_session': {'icon': '✨', 'title': 'Perfectionist',    'desc': 'Get 100% in a session'},
    'speed_demon':     {'icon': '⏱️', 'title': 'Speed Demon',      'desc': 'Complete a timer session'},
    'sessions_10':     {'icon': '📚', 'title': 'Dedicated',        'desc': 'Complete 10 study sessions'},
    'sessions_50':     {'icon': '🎓', 'title': 'Scholar',          'desc': 'Complete 50 study sessions'},
    'word_master':     {'icon': '🔤', 'title': 'Word Master',      'desc': 'Complete 10 word mode sessions'},
}

# ── Kana samples for landing ──────────────────────────────────────────────────
KANA_SAMPLES = [
    {'char': 'あ', 'rom': 'a'},  {'char': 'か', 'rom': 'ka'},
    {'char': 'さ', 'rom': 'sa'}, {'char': 'ア', 'rom': 'a'},
    {'char': 'カ', 'rom': 'ka'}, {'char': '字', 'rom': 'ji'},
    {'char': 'な', 'rom': 'na'}, {'char': 'は', 'rom': 'ha'},
    {'char': 'ま', 'rom': 'ma'},
]

# ── Hiragana ──────────────────────────────────────────────────────────────────
HIRAGANA = [
    {'char': 'あ', 'rom': 'a',   'group': 'vowels'},
    {'char': 'い', 'rom': 'i',   'group': 'vowels'},
    {'char': 'う', 'rom': 'u',   'group': 'vowels'},
    {'char': 'え', 'rom': 'e',   'group': 'vowels'},
    {'char': 'お', 'rom': 'o',   'group': 'vowels'},
    {'char': 'か', 'rom': 'ka',  'group': 'k'},
    {'char': 'き', 'rom': 'ki',  'group': 'k'},
    {'char': 'く', 'rom': 'ku',  'group': 'k'},
    {'char': 'け', 'rom': 'ke',  'group': 'k'},
    {'char': 'こ', 'rom': 'ko',  'group': 'k'},
    {'char': 'さ', 'rom': 'sa',  'group': 's'},
    {'char': 'し', 'rom': 'shi', 'group': 's'},
    {'char': 'す', 'rom': 'su',  'group': 's'},
    {'char': 'せ', 'rom': 'se',  'group': 's'},
    {'char': 'そ', 'rom': 'so',  'group': 's'},
    {'char': 'た', 'rom': 'ta',  'group': 't'},
    {'char': 'ち', 'rom': 'chi', 'group': 't'},
    {'char': 'つ', 'rom': 'tsu', 'group': 't'},
    {'char': 'て', 'rom': 'te',  'group': 't'},
    {'char': 'と', 'rom': 'to',  'group': 't'},
    {'char': 'な', 'rom': 'na',  'group': 'n'},
    {'char': 'に', 'rom': 'ni',  'group': 'n'},
    {'char': 'ぬ', 'rom': 'nu',  'group': 'n'},
    {'char': 'ね', 'rom': 'ne',  'group': 'n'},
    {'char': 'の', 'rom': 'no',  'group': 'n'},
    {'char': 'は', 'rom': 'ha',  'group': 'h'},
    {'char': 'ひ', 'rom': 'hi',  'group': 'h'},
    {'char': 'ふ', 'rom': 'fu',  'group': 'h'},
    {'char': 'へ', 'rom': 'he',  'group': 'h'},
    {'char': 'ほ', 'rom': 'ho',  'group': 'h'},
    {'char': 'ま', 'rom': 'ma',  'group': 'm'},
    {'char': 'み', 'rom': 'mi',  'group': 'm'},
    {'char': 'む', 'rom': 'mu',  'group': 'm'},
    {'char': 'め', 'rom': 'me',  'group': 'm'},
    {'char': 'も', 'rom': 'mo',  'group': 'm'},
    {'char': 'や', 'rom': 'ya',  'group': 'y'},
    {'char': 'ゆ', 'rom': 'yu',  'group': 'y'},
    {'char': 'よ', 'rom': 'yo',  'group': 'y'},
    {'char': 'ら', 'rom': 'ra',  'group': 'r'},
    {'char': 'り', 'rom': 'ri',  'group': 'r'},
    {'char': 'る', 'rom': 'ru',  'group': 'r'},
    {'char': 'れ', 'rom': 're',  'group': 'r'},
    {'char': 'ろ', 'rom': 'ro',  'group': 'r'},
    {'char': 'わ', 'rom': 'wa',  'group': 'w'},
    {'char': 'を', 'rom': 'wo',  'group': 'w'},
    {'char': 'ん', 'rom': 'n',   'group': 'n2'},
]

# ── Katakana ──────────────────────────────────────────────────────────────────
KATAKANA = [
    {'char': 'ア', 'rom': 'a',   'group': 'vowels'},
    {'char': 'イ', 'rom': 'i',   'group': 'vowels'},
    {'char': 'ウ', 'rom': 'u',   'group': 'vowels'},
    {'char': 'エ', 'rom': 'e',   'group': 'vowels'},
    {'char': 'オ', 'rom': 'o',   'group': 'vowels'},
    {'char': 'カ', 'rom': 'ka',  'group': 'k'},
    {'char': 'キ', 'rom': 'ki',  'group': 'k'},
    {'char': 'ク', 'rom': 'ku',  'group': 'k'},
    {'char': 'ケ', 'rom': 'ke',  'group': 'k'},
    {'char': 'コ', 'rom': 'ko',  'group': 'k'},
    {'char': 'サ', 'rom': 'sa',  'group': 's'},
    {'char': 'シ', 'rom': 'shi', 'group': 's'},
    {'char': 'ス', 'rom': 'su',  'group': 's'},
    {'char': 'セ', 'rom': 'se',  'group': 's'},
    {'char': 'ソ', 'rom': 'so',  'group': 's'},
    {'char': 'タ', 'rom': 'ta',  'group': 't'},
    {'char': 'チ', 'rom': 'chi', 'group': 't'},
    {'char': 'ツ', 'rom': 'tsu', 'group': 't'},
    {'char': 'テ', 'rom': 'te',  'group': 't'},
    {'char': 'ト', 'rom': 'to',  'group': 't'},
    {'char': 'ナ', 'rom': 'na',  'group': 'n'},
    {'char': 'ニ', 'rom': 'ni',  'group': 'n'},
    {'char': 'ヌ', 'rom': 'nu',  'group': 'n'},
    {'char': 'ネ', 'rom': 'ne',  'group': 'n'},
    {'char': 'ノ', 'rom': 'no',  'group': 'n'},
    {'char': 'ハ', 'rom': 'ha',  'group': 'h'},
    {'char': 'ヒ', 'rom': 'hi',  'group': 'h'},
    {'char': 'フ', 'rom': 'fu',  'group': 'h'},
    {'char': 'ヘ', 'rom': 'he',  'group': 'h'},
    {'char': 'ホ', 'rom': 'ho',  'group': 'h'},
    {'char': 'マ', 'rom': 'ma',  'group': 'm'},
    {'char': 'ミ', 'rom': 'mi',  'group': 'm'},
    {'char': 'ム', 'rom': 'mu',  'group': 'm'},
    {'char': 'メ', 'rom': 'me',  'group': 'm'},
    {'char': 'モ', 'rom': 'mo',  'group': 'm'},
    {'char': 'ヤ', 'rom': 'ya',  'group': 'y'},
    {'char': 'ユ', 'rom': 'yu',  'group': 'y'},
    {'char': 'ヨ', 'rom': 'yo',  'group': 'y'},
    {'char': 'ラ', 'rom': 'ra',  'group': 'r'},
    {'char': 'リ', 'rom': 'ri',  'group': 'r'},
    {'char': 'ル', 'rom': 'ru',  'group': 'r'},
    {'char': 'レ', 'rom': 're',  'group': 'r'},
    {'char': 'ロ', 'rom': 'ro',  'group': 'r'},
    {'char': 'ワ', 'rom': 'wa',  'group': 'w'},
    {'char': 'ヲ', 'rom': 'wo',  'group': 'w'},
    {'char': 'ン', 'rom': 'n',   'group': 'n2'},
]

# ── Words for Word Mode ───────────────────────────────────────────────────────
WORDS = [
    {'kana': 'あお', 'rom': 'ao', 'meaning': 'blue'},
    {'kana': 'いぬ', 'rom': 'inu', 'meaning': 'dog'},
    {'kana': 'うみ', 'rom': 'umi', 'meaning': 'sea'},
    {'kana': 'えき', 'rom': 'eki', 'meaning': 'station'},
    {'kana': 'おか', 'rom': 'oka', 'meaning': 'hill'},
    {'kana': 'かわ', 'rom': 'kawa', 'meaning': 'river'},
    {'kana': 'きた', 'rom': 'kita', 'meaning': 'north'},
    {'kana': 'くも', 'rom': 'kumo', 'meaning': 'cloud'},
    {'kana': 'けさ', 'rom': 'kesa', 'meaning': 'this morning'},
    {'kana': 'こえ', 'rom': 'koe', 'meaning': 'voice'},
    {'kana': 'さかな', 'rom': 'sakana', 'meaning': 'fish'},
    {'kana': 'しろ', 'rom': 'shiro', 'meaning': 'white'},
    {'kana': 'すし', 'rom': 'sushi', 'meaning': 'sushi'},
    {'kana': 'せかい', 'rom': 'sekai', 'meaning': 'world'},
    {'kana': 'そら', 'rom': 'sora', 'meaning': 'sky'},
    {'kana': 'たいよう', 'rom': 'taiyou', 'meaning': 'sun'},
    {'kana': 'ちず', 'rom': 'chizu', 'meaning': 'map'},
    {'kana': 'つき', 'rom': 'tsuki', 'meaning': 'moon'},
    {'kana': 'てがみ', 'rom': 'tegami', 'meaning': 'letter'},
    {'kana': 'とり', 'rom': 'tori', 'meaning': 'bird'},
    {'kana': 'なつ', 'rom': 'natsu', 'meaning': 'summer'},
    {'kana': 'にほん', 'rom': 'nihon', 'meaning': 'Japan'},
    {'kana': 'ねこ', 'rom': 'neko', 'meaning': 'cat'},
    {'kana': 'のみもの', 'rom': 'nomimono', 'meaning': 'drink'},
    {'kana': 'はな', 'rom': 'hana', 'meaning': 'flower'},
    {'kana': 'ひと', 'rom': 'hito', 'meaning': 'person'},
    {'kana': 'ふゆ', 'rom': 'fuyu', 'meaning': 'winter'},
    {'kana': 'へや', 'rom': 'heya', 'meaning': 'room'},
    {'kana': 'ほし', 'rom': 'hoshi', 'meaning': 'star'},
    {'kana': 'まち', 'rom': 'machi', 'meaning': 'town'},
    {'kana': 'みず', 'rom': 'mizu', 'meaning': 'water'},
    {'kana': 'むし', 'rom': 'mushi', 'meaning': 'insect'},
    {'kana': 'めだま', 'rom': 'medama', 'meaning': 'eyeball'},
    {'kana': 'もり', 'rom': 'mori', 'meaning': 'forest'},
    {'kana': 'やま', 'rom': 'yama', 'meaning': 'mountain'},
    {'kana': 'ゆき', 'rom': 'yuki', 'meaning': 'snow'},
    {'kana': 'よる', 'rom': 'yoru', 'meaning': 'night'},
    {'kana': 'らいねん', 'rom': 'rainen', 'meaning': 'next year'},
    {'kana': 'りんご', 'rom': 'ringo', 'meaning': 'apple'},
    {'kana': 'るす', 'rom': 'rusu', 'meaning': 'absence'},
    {'kana': 'れきし', 'rom': 'rekishi', 'meaning': 'history'},
    {'kana': 'ろうか', 'rom': 'rouka', 'meaning': 'corridor'},
    {'kana': 'わたし', 'rom': 'watashi', 'meaning': 'I / me'},
    {'kana': 'アイス', 'rom': 'aisu', 'meaning': 'ice cream'},
    {'kana': 'カメラ', 'rom': 'kamera', 'meaning': 'camera'},
    {'kana': 'コーヒー', 'rom': 'koohii', 'meaning': 'coffee'},
    {'kana': 'テレビ', 'rom': 'terebi', 'meaning': 'TV'},
    {'kana': 'バス', 'rom': 'basu', 'meaning': 'bus'},
    {'kana': 'パン', 'rom': 'pan', 'meaning': 'bread'},
    {'kana': 'ホテル', 'rom': 'hoteru', 'meaning': 'hotel'},
    {'kana': 'ラジオ', 'rom': 'rajio', 'meaning': 'radio'},
    {'kana': 'レストラン', 'rom': 'resutoran', 'meaning': 'restaurant'},
    {'kana': 'ノート', 'rom': 'nooto', 'meaning': 'notebook'},
    {'kana': 'ゲーム', 'rom': 'geemu', 'meaning': 'game'},
    {'kana': 'スポーツ', 'rom': 'supootsu', 'meaning': 'sports'},
    {'kana': 'ミュージック', 'rom': 'myuujikku', 'meaning': 'music'},
    {'kana': 'インターネット', 'rom': 'intaanetto', 'meaning': 'internet'},
]

SCRIPTS = {
    'hiragana': HIRAGANA,
    'katakana': KATAKANA,
    'kana': HIRAGANA + KATAKANA,
    'kanji': KANJI,
}


# ── SM-2 Spaced Repetition ────────────────────────────────────────────────────
def update_sm2(obj, correct):
    if correct:
        obj.interval = 3 if obj.interval == 1 else (7 if obj.interval == 3 else round(obj.interval * obj.ease_factor))
        obj.ease_factor = max(1.3, obj.ease_factor + 0.1)
    else:
        obj.interval = 1
        obj.ease_factor = max(1.3, obj.ease_factor - 0.2)
    obj.next_review = timezone.now().date() + timedelta(days=obj.interval)
    return obj


# ── Achievement checker ───────────────────────────────────────────────────────
def check_achievements(user, profile, session, results):
    earned = []
    existing = set(Achievement.objects.filter(user=user).values_list('key', flat=True))

    def award(key):
        if key not in existing:
            Achievement.objects.create(user=user, key=key)
            existing.add(key)
            earned.append({**ACHIEVEMENTS[key], 'key': key})

    total_sessions = StudySession.objects.filter(user=user).count()
    if total_sessions >= 1: award('first_session')
    if total_sessions >= 10: award('sessions_10')
    if total_sessions >= 50: award('sessions_50')
    if profile.streak_days >= 3: award('streak_3')
    if profile.streak_days >= 7: award('streak_7')
    if profile.streak_days >= 30: award('streak_30')
    if profile.total_xp >= 100: award('xp_100')
    if profile.total_xp >= 500: award('xp_500')
    if profile.total_xp >= 1000: award('xp_1000')
    if results and all(r['correct'] for r in results): award('perfect_session')
    if session.mode == 'timer': award('speed_demon')
    if CharacterProgress.objects.filter(user=user, script='hiragana', mastered=True).count() >= 46: award('hiragana_done')
    if CharacterProgress.objects.filter(user=user, script='katakana', mastered=True).count() >= 46: award('katakana_done')
    if CharacterProgress.objects.filter(user=user, script='kanji', mastered=True).count() >= 50: award('kanji_50')
    word_sessions = StudySession.objects.filter(user=user, mode='word').count()
    if word_sessions >= 10: award('word_master')
    return earned


# ── Views ─────────────────────────────────────────────────────────────────────

def landing(request):
    if request.user.is_authenticated:
        return redirect('/learn/')
    return render(request, 'core/landing.html', {'kana_samples': KANA_SAMPLES})


@login_required
def home(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    hiragana_mastered = CharacterProgress.objects.filter(user=user, script='hiragana', mastered=True).count()
    katakana_mastered = CharacterProgress.objects.filter(user=user, script='katakana', mastered=True).count()
    kanji_mastered = CharacterProgress.objects.filter(user=user, script='kanji', mastered=True).count()
    recent_sessions = StudySession.objects.filter(user=user).order_by('-created_at')[:5]
    context = {
        'profile': profile,
        'hiragana_mastered': hiragana_mastered,
        'hiragana_total': len(HIRAGANA),
        'katakana_mastered': katakana_mastered,
        'katakana_total': len(KATAKANA),
        'kanji_mastered': kanji_mastered,
        'kanji_total': len(KANJI),
        'recent_sessions': recent_sessions,
        'total_mastered': hiragana_mastered + katakana_mastered + kanji_mastered,
        'total_chars': len(HIRAGANA) + len(KATAKANA) + len(KANJI),
    }
    return render(request, 'core/home.html', context)


@login_required
def chart(request):
    context = {
        'hiragana': HIRAGANA,
        'katakana': KATAKANA,
        'hiragana_json': json.dumps(HIRAGANA),
        'katakana_json': json.dumps(KATAKANA),
    }
    return render(request, 'core/chart.html', context)


@login_required
def practice(request):
    context = {
        'hiragana_json': json.dumps(HIRAGANA),
        'katakana_json': json.dumps(KATAKANA),
        'kana_json': json.dumps(HIRAGANA + KATAKANA),
        'kanji_json': json.dumps(KANJI),
    }
    return render(request, 'core/practice.html', context)


@login_required
def word_mode(request):
    context = {
        'words_json': json.dumps(WORDS),
        'total': len(WORDS),
    }
    return render(request, 'core/wordmode.html', context)


@login_required
@require_POST
def save_progress(request):
    try:
        data = json.loads(request.body)
        script = data.get('script')
        results = data.get('results', [])
        correct = data.get('correct', 0)
        incorrect = data.get('incorrect', 0)
        mode = data.get('mode', 'normal')
        xp = correct * 10
        if mode == 'timer': xp = int(xp * 1.5)

        for r in results:
            obj, _ = CharacterProgress.objects.get_or_create(
                user=request.user, script=script, character=r['char'],
                defaults={'romanji': r['rom']}
            )
            if r['correct']: obj.correct_count += 1
            else: obj.incorrect_count += 1
            obj.mastered = obj.correct_count >= 3
            obj.romanji = r['rom']
            obj = update_sm2(obj, r['correct'])
            obj.save()

        session = StudySession.objects.create(
            user=request.user, script=script,
            correct=correct, incorrect=incorrect, xp_earned=xp, mode=mode,
        )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.total_xp += xp
        today = timezone.now().date()
        if profile.last_study_date and (today - profile.last_study_date).days == 1:
            profile.streak_days += 1
        elif profile.last_study_date != today:
            profile.streak_days = 1
        profile.last_study_date = today
        profile.save()

        new_achievements = check_achievements(request.user, profile, session, results)
        return JsonResponse({'status': 'ok', 'xp_earned': xp, 'new_achievements': new_achievements})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    hiragana_mastered = CharacterProgress.objects.filter(user=user, script='hiragana', mastered=True).count()
    katakana_mastered = CharacterProgress.objects.filter(user=user, script='katakana', mastered=True).count()
    kanji_mastered = CharacterProgress.objects.filter(user=user, script='kanji', mastered=True).count()
    all_sessions = StudySession.objects.filter(user=user).order_by('-created_at')
    today = timezone.now().date()
    xp_chart = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        day_xp = sum(s.xp_earned for s in all_sessions if s.created_at.date() == day)
        xp_chart.append({'date': day.strftime('%b %d'), 'xp': day_xp})
    earned_keys = set(Achievement.objects.filter(user=user).values_list('key', flat=True))
    achievements_list = [{**data, 'key': key, 'earned': key in earned_keys} for key, data in ACHIEVEMENTS.items()]
    context = {
        'profile': profile,
        'hiragana_mastered': hiragana_mastered, 'hiragana_total': len(HIRAGANA),
        'katakana_mastered': katakana_mastered, 'katakana_total': len(KATAKANA),
        'kanji_mastered': kanji_mastered, 'kanji_total': len(KANJI),
        'total_mastered': hiragana_mastered + katakana_mastered + kanji_mastered,
        'total_chars': len(HIRAGANA) + len(KATAKANA) + len(KANJI),
        'all_sessions': all_sessions[:10],
        'total_sessions': all_sessions.count(),
        'xp_chart_json': json.dumps(xp_chart),
        'achievements': achievements_list,
        'earned_count': len(earned_keys),
        'total_achievements': len(ACHIEVEMENTS),
    }
    return render(request, 'core/profile.html', context)


@login_required
def leaderboard(request):
    from django.contrib.auth.models import User
    top_users = UserProfile.objects.select_related('user').order_by('-total_xp')[:20]
    context = {
        'top_users': top_users,
        'current_profile': UserProfile.objects.get_or_create(user=request.user)[0],
    }
    return render(request, 'core/leaderboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')
