from utils.custom_view import APIView
from utils.change_datetime import change_datetime_notice
from .models import Notice, Question, Answer
from .serializers import NoticeSerializer, QuestionSerializer, AnswerSerializer
from django.core.exceptions import ObjectDoesNotExist
import logging


logger = logging.getLogger(__name__)


class NoticeAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = Notice.objects.get(id=pk)
            serializer = NoticeSerializer(queryset)
            result = change_datetime_notice(data=serializer.data)
            logger.debug('Request Detail Success : {0} (군번 : {1})'.format('공지사항 요청 성공',
                                                                          request.user.srvno))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Detail Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('공지사항 요청 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')


class NoticeListAPI(APIView):
    def get(self, request):
        try:
            queryset = Notice.objects.all()
            serializer = NoticeSerializer(queryset, many=True)
            result = change_datetime_notice(data=serializer.data)
            logger.debug('Request List Success : {0} (군번 : {1})'.format('공지사항 목록 요청 성공',
                                                                        request.user.srvno))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('공지사항 목록 요청 실패',
                                                                                 request.user.srvno,
                                                                                 e))
            return self.fail(message='fail')


class QuestionAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = Question.objects.get(id=pk)
            serializer = QuestionSerializer(queryset)
            result = change_datetime_notice(data=serializer.data)
            logger.debug('Request Detail Success : {0} (군번 : {1})'.format('질문 요청 성공',
                                                                          request.user.srvno))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Detail Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('질문 요청 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')

    def put(self, request, pk=None):
        try:
            queryset = Question.objects.get(id=pk)
            serializer = QuestionSerializer(queryset, data=request.data)
            if serializer.is_valid():
                serializer.save()
            logger.debug('Request Update Success : {0} (군번 : {1})'.format('질문 수정 성공',
                                                                          request.user.srvno))
            return self.success(message='success')

        except Exception as e:
            logger.debug('Request Update Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('질문 수정 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')

    def delete(self, request, pk=None):
        try:
            queryset = Question.objects.get(id=pk)
            queryset.delete()
            logger.debug('Request Delete Success : {0} (군번 : {1})'.format('질문 삭제 성공',
                                                                          request.user.srvno))
            return self.success(message='success')

        except Exception as e:
            logger.debug('Request Delete Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('질문 삭제 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')


class QuestionCreateAPI(APIView):
    def post(self, request):
        try:
            obj = Question.objects.create(title=request.data['title'],
                                          content=request.data['content'],
                                          types=request.data['types'],
                                          writer=request.user)
            obj.save()
            logger.debug('Request Create Success : {0} (군번 : {1})'.format('질문 작성 성공',
                                                                          request.user.srvno))
            return self.success(message='success')
        except Exception as e:
            logger.debug('Request Create Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('질문 작성 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')


class QuestionListAPI(APIView):
    def get(self, request):
        try:
            queryset = Question.objects.filter(writer=request.user)
            serializer = QuestionSerializer(queryset, many=True)
            logger.debug('Request List Success : {0} (군번 : {1})'.format('질문 목록 요청 성공',
                                                                        request.user.srvno))
            return self.success(data=serializer.data, message='success')

        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('질문 목록 요청 실패',
                                                                                 request.user.srvno,
                                                                                 e))
            return self.fail(message='fail')


class AnswerAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = Answer.objects.get(q_id=pk)
            serializer = AnswerSerializer(queryset)
            result = change_datetime_notice(data=serializer.data)
            logger.debug('Request Detail Success : {0} (군번 : {1})'.format('답변 요청 성공',
                                                                          request.user.srvno))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Detail Fail : {0} (군번 : {1}, 오류 내용 : {2}'.format('답변 요청 실패',
                                                                                   request.user.srvno,
                                                                                   e))
            return self.fail(message='fail')
