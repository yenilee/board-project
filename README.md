# Board-project
flask &amp; mongodb 활용 게시판 프로젝트

1. [stack we used](#stack)
2. [package manager](#package)
3. [spec](#spec)

## <a name="stack"></a>Stack we used  
- Flask
- Flask-classful
- mashmallow
- MongoEngine

## <a name="package"></a>Package manager
- Poetry

## <a name="spec"></a>spec
- 회원
    - 회원가입
    - 로그인
- 게시판
    - 게시판 목록(category)
    - 게시판 CRUD
    - 게시판 내 게시글 검색(제목, 사용자, 태그)
- 게시글
    - 게시글 CRUD 
    - 게시글 태그 추가
    - 댓글, 대댓글(1depth) CRUD
    - 좋아요(글, 댓글, 대댓글)
- 메인페이지
    - 좋아요 많은 글 10개
    - 댓글 많은 글 10개
    - 최신 글 10개
- 마이페이지
    - 내가 쓴 글
    - 내가 쓴 댓글
    - 내가 좋아요한글
