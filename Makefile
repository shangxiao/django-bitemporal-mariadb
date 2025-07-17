.PHONY: tags

runserver:
	./manage.py runserver

tags:
	ctags -R --languages=Python .
