"""korea_tools 순수 함수 자체 검증. `python test_tools.py` 로 실행."""

import korea_tools as kt


def check(label, got, expected):
    ok = got == expected
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: got={got!r}" + ("" if ok else f" expected={expected!r}"))
    return ok


def main():
    results = []

    # 자모 분해 / 초성
    results.append(check("chosung 한국어", kt.chosung("한국어"), "ㅎㄱㅇ"))
    d = kt.decompose_hangul("값")
    results.append(check("decompose 값 종성", d["syllables"][0]["jong"], "ㅄ"))
    results.append(check("compose ㅎㅏㄴ", kt.compose_hangul("ㅎ", "ㅏ", "ㄴ")["char"], "한"))

    # 로마자
    results.append(check("romanize 한국", kt.romanize("한국")["romanized"], "hanguk"))
    results.append(check("romanize 서울", kt.romanize("서울")["romanized"], "seoul"))
    results.append(check("romanize 김치", kt.romanize("김치")["romanized"], "gimchi"))
    results.append(check("romanize 음악(연음)", kt.romanize("음악")["romanized"], "eumak"))
    # 자음동화
    results.append(check("romanize 종로", kt.romanize("종로")["romanized"], "jongno"))
    results.append(check("romanize 신라", kt.romanize("신라")["romanized"], "silla"))
    results.append(check("romanize 설날", kt.romanize("설날")["romanized"], "seollal"))
    results.append(check("romanize 국민", kt.romanize("국민")["romanized"], "gungmin"))
    results.append(check("romanize 백마", kt.romanize("백마")["romanized"], "baengma"))
    results.append(check("romanize 협력", kt.romanize("협력")["romanized"], "hyeomnyeok"))
    results.append(check("romanize 독립", kt.romanize("독립")["romanized"], "dongnip"))
    results.append(check("romanize 왕십리", kt.romanize("왕십리")["romanized"], "wangsimni"))

    # 숫자 <-> 한글
    results.append(check("num->kor 12345", kt.number_to_korean(12345)["korean"], "일만이천삼백사십오"))
    results.append(check("num->kor 0", kt.number_to_korean(0)["korean"], "영"))
    results.append(check("num->kor 105", kt.number_to_korean(105)["korean"], "백오"))
    results.append(check("num->kor formal 12345",
                         kt.number_to_korean(12345, "formal")["korean"], "금 일만이천삼백사십오원정"))
    results.append(check("num->kor 100000000", kt.number_to_korean(100000000)["korean"], "일억"))
    results.append(check("kor->num 일만이천삼백사십오",
                         kt.korean_to_number("일만이천삼백사십오")["number"], 12345))
    results.append(check("kor->num roundtrip 987654321",
                         kt.korean_to_number(kt.number_to_korean(987654321)["korean"])["number"], 987654321))

    # 사업자등록번호 (공개된 유효 예시 체크섬)
    results.append(check("biz 220-81-62517 valid",
                         kt.validate_business_number("220-81-62517")["valid"], True))
    results.append(check("biz 123-45-67890 invalid",
                         kt.validate_business_number("123-45-67890")["valid"], False))

    # 주민등록번호 형식 (성별/세기 추출; 임의 숫자라 checksum은 검증만)
    r = kt.validate_rrn("900101-1234567")
    results.append(check("rrn birth", r.get("birth_date"), "1990-01-01"))
    results.append(check("rrn gender", r.get("gender"), "남"))

    # 공휴일 / 영업일
    h = kt.korean_holidays(2026)
    results.append(check("holiday 2026 has 신정", any(x["name"] == "신정" for x in h["holidays"]), True))
    b = kt.business_days_between("2026-01-01", "2026-01-07")  # 목~수, 1/1 신정 공휴일
    results.append(check("business days 2026-01-01..07", b["business_days"], 4))

    # D-day
    results.append(check("d_day", kt.d_day("2026-07-20", "2026-07-14")["label"], "D-6"))

    # 전화번호
    results.append(check("phone 휴대전화", kt.format_phone_number("01012345678")["formatted"], "010-1234-5678"))
    results.append(check("phone 서울 지역", kt.format_phone_number("0212345678")["region"], "서울"))
    results.append(check("phone 부산 지역", kt.format_phone_number("051-123-4567")["region"], "부산"))
    results.append(check("phone 대표번호", kt.format_phone_number("15881234")["kind"], "전국대표번호"))

    # 면적
    results.append(check("area 34평->m2", kt.area_convert(34, "pyeong")["m2"], round(34 * (400 / 121), 4)))
    results.append(check("area 84m2->평", kt.area_convert(84, "m2")["pyeong"], round(84 / (400 / 121), 4)))

    # 만 나이
    a = kt.korean_age("1990-08-01", "2026-07-14")  # 생일 전
    results.append(check("age man(생일전)", a["manAge"], 35))
    results.append(check("age year", a["yearAge"], 36))
    a2 = kt.korean_age("1990-07-01", "2026-07-14")  # 생일 후
    results.append(check("age man(생일후)", a2["manAge"], 36))

    # 원화 포맷
    results.append(check("won_format", kt.won_format(1234567)["text"], "1,234,567원"))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
