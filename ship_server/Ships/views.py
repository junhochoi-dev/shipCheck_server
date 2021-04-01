from utils.custom_view import APIView
from .models import NormalShip, NormalImage, WasteShip, WasteImage
from Accounts.models import Account
from .serializers import (NormalShipSerializer, NormalImageSerializer, WasteShipSerializer,
                          WasteImageSerializer, WasteLocationSerializer, NormalLocationSerializer,
                          NormalShipUpdateSerializer, WasteShipUpdateSerializer,
                          ProgramNormalShipSerializer, ProgramWasteShipSerializer,)
from django.core.exceptions import ObjectDoesNotExist
import numpy as np
from django.core.files import File
import base64
from django.core.files.base import ContentFile
from keras_model.prediction_ship import ai_module
from PIL import Image
from io import BytesIO
import uuid
import io
from utils.best_three import best_three
from rest_framework.permissions import AllowAny
import pandas as pd
from datetime import datetime
import time
import os
import csv
import logging
import random
from utils.change_format import change_datetime
from django.shortcuts import render


logger = logging.getLogger(__name__)


class DetailNormalShipAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = NormalShip.objects.get(id=pk)
            serializer = NormalShipSerializer(queryset)
            result = change_datetime(data=serializer.data)
            logger.debug('Request Detail Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 정보 요청 성공',
                                                                                     request.user.srvno,
                                                                                     pk))
            return self.success(data=result, message='success')
        except ObjectDoesNotExist:
            logger.debug('Request Detail Fail : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 정보 요청 실패, 존재하지 않는 선박 ',
                                                                                  request.user.srvno,
                                                                                  pk))
            return self.fail(message='Not Exist')

    def delete(self, request, pk=None):
        if request.user.user_level >= 2:
            try:
                queryset = NormalShip.objects.get(id=pk)
                logger.debug('Request Delete Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 제거 요청 성공',
                                                                                         request.user.srvno,
                                                                                         queryset))
                queryset.delete()
                return self.success(message='success')
            except ObjectDoesNotExist:
                logger.debug('Request Delete Fail : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 제거 요청 실패, 존재하지 않는 선박',
                                                                                      request.user.srvno,
                                                                                      pk))
                return self.fail(message='Not Exist')
        else:
            return self.fail(message='No permission')

    def post(self, request, pk=None):
        if request.user.user_level >= 2:
            try:
                queryset = NormalShip.objects.get(id=pk)
                serializer = NormalShipUpdateSerializer(queryset, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    logger.debug('Request Update Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 수정 요청 성공',
                                                                                             request.user.srvno,
                                                                                             request.data))
                    return self.success(message='success')
                else:
                    logger.debug('Request Update Fail : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 수정 요청 실패, 유효하지 않은 데이터',
                                                                                          request.user.srvno,
                                                                                          request.data))
                    return self.fail(message='fail')
            except ObjectDoesNotExist:
                logger.debug('Request Update Fail : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 수정 요청 실패, 존재하지 않는 선박',
                                                                                      request.user.srvno,
                                                                                      request.data))
                return self.fail(message='fail')
        else:
            return self.fail(message='No Permission')


class CreateNormalShipAPI(APIView):
    def post(self, request):
        try:
            ship_id = NormalShip.create_normal_ship(data=request.data, user=request.user)
            if len(request.data['image_data']) > 1:
                NormalImage.create_normal_image(img_list=request.data['image_data'],
                                                ship_id=ship_id,
                                                user=request.user)
            logger.debug('Request Create Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 등록 요청 성공',
                                                                                     request.user.srvno,
                                                                                     request.data))
            return self.success(message='success')
        except Exception as e:
            logger.debug('Request Create Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '일반 선박 등록 요청 실패, 유효하지 않은 데이터',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class ListNormalShipAPI(APIView):
    def get(self, request):
        page = int(request.GET.get('page'))
        try:
            query_size = NormalShip.objects.count()
            page_size = 10
            if query_size % page_size == 0:
                count = int(query_size / page_size)
            else:
                count = int(query_size / page_size) + 1
            if page is 1:
                queryset = NormalShip.objects.all()[0:page_size]
            elif page is count:
                start = page_size * (page - 1)
                queryset = NormalShip.objects.all()[start:]
            else:
                start = page_size * (page - 1)
                end = start + page_size
                queryset = NormalShip.objects.all()[start:end]
            serializer = NormalShipSerializer(queryset, many=True)
            data = change_datetime(serializer.data)
            result = {"count": count, "data": data}
            logger.debug('Request List Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 목록 요청 성공',
                                                                                   request.user.srvno,
                                                                                   page))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류내용 : {2})'.format('일반 선박 목록 요청 실패, 유효하지 않은 데이터',
                                                                                 request.user.srvno,
                                                                                 e))
            return self.fail(message='fail')


class SearchNormalShipAPI(APIView):
    def post(self, request):
        try:
            queryset = NormalShip.searching_normal_ship(data=request.data)
            query_size = queryset.count()
            page_size = 10
            page = int(request.GET.get('page'))
            if query_size % page_size == 0:
                count = int(query_size / page_size)
            else:
                count = int(query_size / page_size) + 1
            if page is 1:
                queryset = queryset[0:page_size]
            elif page is count:
                start = page_size * (page - 1)
                queryset = queryset[start:]
            else:
                start = page_size * (page - 1)
                end = start + page_size
                queryset = queryset[start:end]
            serializer = NormalShipSerializer(queryset, many=True)
            result = {'count': count, "data": serializer.data}
            logger.debug('Request Search Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 검색 요청 성공',
                                                                                     request.user.srvno,
                                                                                     request.data))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Search Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '일반 선박 검색 요청 실패, 유효하지 않은 데이터',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class DetailWasteShipAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = WasteShip.objects.get(id=pk)
            serializer = WasteShipSerializer(queryset)
            result = change_datetime(serializer.data)
            logger.debug('Request Detail Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 정보 요청 성공',
                                                                                     request.user.srvno,
                                                                                     request.data))
            return self.success(data=result, message='success')
        except ObjectDoesNotExist:
            logger.debug('Request Detail Fail : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 정보 요청 실패, 존재하지 않는 선박',
                                                                                  request.user.srvno,
                                                                                  pk))
            return self.fail(message='Not Exist')

    def delete(self, request, pk=None):
        if request.user.user_level >= 2:
            try:
                queryset = WasteShip.objects.get(id=pk)
                logger.debug('Request Delete Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 제거 요청 성공',
                                                                                         request.user.srvno,
                                                                                         queryset))
                queryset.delete()
                return self.success(message='success')
            except ObjectDoesNotExist:
                logger.debug('Request Delete Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 제거 요청 실패, 존재하지 않는 선박',
                                                                                         request.user.srvno,
                                                                                         request.data))
                return self.fail(message='Not Exist')
        else:
            return self.fail(message='No permission')

    def post(self, request, pk=None):
        if request.user.user_level >= 2:
            try:
                queryset = WasteShip.objects.get(id=pk)
                serializer = WasteShipUpdateSerializer(queryset, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    logger.debug('Request Update Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 수정 요청 성공',
                                                                                             request.user.srvno,
                                                                                             request.data))
                    return self.success(message='success')
                else:
                    logger.debug('Request Update Fail : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 수정 요청 실패, 유효하지 않은 데이터',
                                                                                          request.user.srvno,
                                                                                          request.data))
                    return self.fail(message='fail')
            except ObjectDoesNotExist:
                logger.debug('Request Update Fail : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 수정 요청 실패, 존재하지 않는 선박',
                                                                                      request.user.srvno,
                                                                                      request.data))
                return self.fail(message='fail')
        else:
            return self.fail(message='No permission')


class CreateWasteShipAPI(APIView):
    def post(self, request):
        try:
            ship_id = WasteShip.create_waste_ship(data=request.data, user=request.user)
            if len(request.data['image_data']) > 1:
                WasteImage.create_waste_image(img_list=request.data['image_data'],
                                              ship_id=ship_id,
                                              user=request.user)
            logger.debug('Request Create Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 등록 요청 성공',
                                                                                     request.user.srvno,
                                                                                     request.data))
            return self.success(message='success')
        except Exception as e:
            logger.debug('Request Create Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '유기 선박 등록 요청 실패, 유효하지 않은 데이터',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class ListWasteShipAPI(APIView):
    def get(self, request):
        page = int(request.GET.get('page'))
        try:
            query_size = WasteShip.objects.count()
            page_size = 10
            if query_size % page_size == 0:
                count = int(query_size / page_size)
            else:
                count = int(query_size / page_size) + 1
            if page is 1:
                queryset = WasteShip.objects.all()[0:page_size]
            elif page is count:
                start = page_size * (page - 1)
                queryset = WasteShip.objects.all()[start:]
            else:
                start = page_size * (page - 1)
                end = start + page_size
                queryset = WasteShip.objects.all()[start:end]
            serializer = WasteShipSerializer(queryset, many=True)
            data = change_datetime(serializer.data)
            result = {'count': count, "data": data}
            logger.debug('Request List Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 목록 요청 성공',
                                                                                   request.user.srvno,
                                                                                   page))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2})'.format('유기 선박 목록 요청 실패, 유효하지 않은 데이터',
                                                                                  request.user.srvno,
                                                                                  e))
            return self.fail(message='fail')


class LocationShipAPI(APIView):
    def get(self, request):
        try:
            w_queryset = WasteShip.objects.all()
            n_queryset = NormalShip.objects.all()
            w_location = WasteLocationSerializer(w_queryset, many=True)
            n_location = NormalLocationSerializer(n_queryset, many=True)
            result = {"normal": n_location.data, "waste": w_location.data}
            logger.debug('Request Location Success : {0} (군번 : {1})'.format('유기 선박 위치 요청 성공', request.user.srvno))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Location Fail : {0} (군번 : {1}, 오류 내용 : {2})'.format('유기 선박 위치 요청 실패, 유효하지 않은 데이터',
                                                                                      request.user.srvno,
                                                                                      e))
            return self.fail(message='fail')


class SearchWasteShipAPI(APIView):
    def post(self, request):
        try:
            queryset = WasteShip.searching_waste_ship(data=request.data)
            query_size = queryset.count()
            page_size = 10
            page = int(request.GET.get('page'))
            if query_size % page_size == 0:
                count = int(query_size / page_size)
            else:
                count = int(query_size / page_size) + 1
            if page is 1:
                queryset = queryset[0:page_size]
            elif page is count:
                start = page_size * (page - 1)
                queryset = queryset[start:]
            else:
                start = page_size * (page - 1)
                end = start + page_size
                queryset = queryset[start:end]
            serializer = WasteShipSerializer(queryset, many=True)
            result = {'count': count, "data": serializer.data}
            logger.debug('Request Search Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 검색 요청 성공',
                                                                                     request.user.srvno,
                                                                                     request.data))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Search Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '유기 선박 검색 요청 실패, 유효하지 않은 데이터',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class ListNormalImageAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = NormalShip.objects.get(id=pk)
            img_queryset = NormalImage.objects.filter(n_name=queryset.id)
            serializer = NormalImageSerializer(img_queryset, many=True)
            logger.debug('Request List Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 이미지 목록 요청 성공',
                                                                                   request.user.srvno,
                                                                                   pk))
            return self.success(data=serializer.data, message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2})'.format('일반 선박 이미지 목록 요청 실패, 유효하지 않은 데이터',
                                                                                  request.user.srvno,
                                                                                  e))
            return self.fail(message='fail')


class AddNormalImageAPI(APIView):
    def post(self, request):
        try:
            NormalImage.add_normal_image(request.data['image_data'], request.data['id'], request.user)
            logger.debug('Request Add Success : {0} (군번 : {1}, 데이터 : {2})'.format('일반 선박 이미지 추가 요청 성공',
                                                                                  request.user.srvno,
                                                                                  request.data))
            return self.success(message='success')
        except Exception as e:
            logger.debug('Request Add Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '일반 선박 이미지 추가 요청 실패, 유효하지 않은 데이터 ',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class ListWasteImageAPI(APIView):
    def get(self, request, pk=None):
        try:
            queryset = WasteImage.objects.get(id=pk)
            img_queryset = WasteImage.objects.filter(w_id=queryset.id)
            serializer = WasteImageSerializer(img_queryset, many=True)
            logger.debug('Request List Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 이미지 목록 요청 성공',
                                                                                   request.user.srvno,
                                                                                   pk))
            return self.success(data=serializer.data, message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2})'.format('유기 선박 이미지 목록 요청 실패, 유효하지 않은 데이터',
                                                                                  request.user.srvno,
                                                                                  e))
            return self.fail(message='fail')


class AddWasteImageAPI(APIView):
    def post(self, request):
        try:
            WasteImage.add_waste_image(request.data['image_data'], request.data['id'], request.user)
            logger.debug('Request List Success : {0} (군번 : {1}, 데이터 : {2})'.format('유기 선박 이미지 추가 요청 성공',
                                                                                   request.user.srvno,
                                                                                   request.data))
            return self.success(message='success')
        except Exception as e:
            logger.debug('Request List Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '유기 선박 이미지 추가 요청 실패, 유효하지 않은 데이터 ',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class PredictShipAPI(APIView):
    def post(self, request):
        try:
            image_data = base64.b64decode(request.data['image_data'])
            img = Image.open(io.BytesIO(image_data))
            data = ai_module(img)
            result_set = best_three(data[0])
            kinds = list()
            if result_set['first'][0][0] is 'n':
                first_ship = NormalShip.objects.get(id=int(result_set['first'][0][2:]))
                first_serial = NormalShipSerializer(first_ship)
                kinds.append(1)
            else:
                first_ship = WasteShip.objects.get(id=int(result_set['first'][0][2:]))
                first_serial = WasteShipSerializer(first_ship)
                kinds.append(0)
            if result_set['second'][0][0] is 'n':
                second_ship = NormalShip.objects.get(id=int(result_set['second'][0][2:]))
                second_serial = NormalShipSerializer(second_ship)
                kinds.append(1)
            else:
                second_ship = WasteShip.objects.get(id=int(result_set['second'][0][2:]))
                second_serial = WasteShipSerializer(second_ship)
                kinds.append(0)
            if result_set['third'][0][0] is 'n':
                third_ship = NormalShip.objects.get(id=int(result_set['third'][0][2:]))
                third_serial = NormalShipSerializer(third_ship)
                kinds.append(1)
            else:
                third_ship = WasteShip.objects.get(id=int(result_set['third'][0][2:]))
                third_serial = WasteShipSerializer(third_ship)
                kinds.append(0)
            first_serial = change_datetime(first_serial.data)
            second_serial = change_datetime(second_serial.data)
            third_serial = change_datetime(third_serial.data)
            result_ship = [first_serial, second_serial, third_serial]
            result = {'result': result_ship, 'kinds': kinds, 'percent': [result_set['first'][1],
                                                                         result_set['second'][1],
                                                                         result_set['third'][1]]}
            logger.debug('Request Predict Success : {0} (군번 : {1}, 데이터 : {2})'.format('선박 AI 요청 성공',
                                                                                      request.user.srvno,
                                                                                      request.data))
            return self.success(data=result, message='success')
        except Exception as e:
            logger.debug('Request Predict Fail : {0} (군번 : {1}, 오류 내용 : {2}, 데이터 : {3})'.format(
                '선박 AI 요청 실패',
                request.user.srvno,
                e,
                request.data))
            return self.fail(message='fail')


class DownloadAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'Ships/download_page.html')


class ProgramNormalShipAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        try:
            queryset = NormalShip.objects.get(id=pk)
            serializer = ProgramNormalShipSerializer(queryset)
            return self.success(data=serializer.data, message='success')
        except ObjectDoesNotExist:
            return self.fail(message='Not Exist')


class ProgramWasteShipAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        try:
            queryset = WasteShip.objects.get(id=pk)
            serializer = ProgramWasteShipSerializer(queryset)
            return self.success(data=serializer.data, message='success')
        except ObjectDoesNotExist:
            return self.fail(message='Not Exist')


class RemoveTrashData(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        trash = NormalShip.objects.get(id=pk)
        base_path = 'D:/shipCheck_server/ship_server/Ships/media/'
        os.remove(base_path + str(trash.main_img))
        trash.delete()
        # queryset = NormalShip.objects.filter(img_cnt__gte=10).order_by('-img_cnt')
        # serializer = NormalShipSerializer(queryset, many=True)
        # f = open('D:/ai보고용/데이터현황.csv', 'w', newline='')
        # idx = 1
        # for data in serializer.data:
        #     name = data['name']
        #     img_cnt = data['img_cnt']
        #     img_list = []
        #     main_img_idx = data['main_img'].find('/22/')
        #     img_list.append(data['main_img'][main_img_idx+4:])
        #     for file in data['normal_imgs']:
        #         main_img_idx = file.find('/22/')
        #         img_list.append(file[main_img_idx + 4:])
        #     wr = csv.writer(f)
        #     wr.writerow([str(idx), name, img_cnt, img_list])
        #     idx = idx + 1
        # f.close()
        return self.success(data=serializer.data, message='success')


class NormalShipRegister(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ship_csv = pd.read_csv('D:/기존 사용 DB/선박.csv')
        img_csv = pd.read_csv('D:/기존 사용 DB/선박이미지.csv')
        black = []
        for ship_id in ship_csv['id']:
            if ship_id in black:
                continue
            search_row = ship_csv.loc[(ship_csv['id'] == ship_id)]
            name = list(search_row['ship_name'])[0]
            code = list(search_row['registerd_ship_num'])[0]
            size = list(search_row['width_length'])[0]
            weight = list(search_row['weight'])[0]
            lat = list(search_row['lat'])[0]
            lon = list(search_row['long'])[0]
            find_row = img_csv.loc[(img_csv['shipdb_id'] == ship_id)]  # 필터링 된 row를 이용하여 img 주소 찾기
            img_len = len(list(find_row['ship_image']))
            if name == 'none' or name == '.' or name == '미상' or name == '':
                name = '정보 없음'
            if code == 'none' or code == '.' or code == '미상' or code == '':
                code = '정보 없음'
            if size == 'none' or name == '.':
                size = '정보 없음'
            if weight == 'none' or name == '':
                weight = '정보 없음'
            if not img_len == 0:
                img_path = list(find_row['ship_image'])
                img = Image.open('D:/기존 사용 DB/media/' + img_path[0])
                img_name = str(uuid.uuid4())
                buf = BytesIO()
                img.save(buf, 'jpeg')
                buf.seek(0)
                img_bytes = buf.read()
                buf.close()
                ship = NormalShip.objects.create(name=name,
                                                 code=code,
                                                 size=size,
                                                 tons=weight,
                                                 img_cnt=img_len,
                                                 register=Account.objects.get(srvno='ADMIN'),
                                                 region='정보 없음',
                                                 lat=lat,
                                                 lon=lon,
                                                 main_img=ContentFile(img_bytes, str(datetime.today())+img_name+'.jpg'))
                if img_len > 1:
                    for i in range(img_len):
                        if i == 0:
                            continue
                        else:
                            img = Image.open('D:/기존 사용 DB/media/' + img_path[i])
                            img_name = str(uuid.uuid4())
                            buf = BytesIO()
                            img.save(buf, 'jpeg')
                            buf.seek(0)
                            img_bytes = buf.read()
                            buf.close()
                            ship_img = NormalImage.objects.create(n_name=NormalShip.objects.get(id=ship.id),
                                                                  img=ContentFile(img_bytes,
                                                                                  str(datetime.today())+img_name+'.jpg'),
                                                                  register=Account.objects.get(srvno='ADMIN'))
                            ship_img.save()
                            print('{0} / {1}'.format(i, img_len))
                print('{} 선박 등록 완료'.format(ship_id))
            else:
                ship = NormalShip.objects.create(name=name,
                                                 code=code,
                                                 size=size,
                                                 tons=weight,
                                                 img_cnt=img_len,
                                                 region='정보 없음',
                                                 register=Account.objects.get(srvno='ADMIN'))
                ship.save()
                print('이미지가 없어요 ㅜㅜ')
                print('{} 선박 등록 완료'.format(ship_id))
        return self.success(message='success')


class WasteShipReigster(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ship_csv = pd.read_csv('D:/기존 사용 DB/유기,폐 선박.csv')
        img_csv = pd.read_csv('D:/기존 사용 DB/유기,폐 선박 이미지.csv')
        for ship_id in ship_csv['id']:
            search_row = ship_csv.loc[(ship_csv['id'] == ship_id)]
            lat = list(search_row['lat'])[0]
            if lat == 'none':
                lat = 0
            lon = list(search_row['long'])[0]
            if lon == 'none':
                lon = 0
            info = list(search_row['info'])[0]
            info = str(info)
            if info is 'nan':
                info = '정보 없음'
            find_row = img_csv.loc[(img_csv['shipdb_id'] == int(ship_id))]  # 필터링 된 row를 이용하여 img 주소 찾기
            img_len = len(list(find_row['ship_image']))
            if not img_len == 0:
                img_path = list(find_row['ship_image'])
                img = Image.open('D:/기존 사용 DB/media/' + img_path[0])
                img_name = str(uuid.uuid4())
                buf = BytesIO()
                img.save(buf, 'jpeg')
                buf.seek(0)
                img_bytes = buf.read()
                buf.close()
                ship = WasteShip.objects.create(lat=lat,
                                                lon=lon,
                                                info=info,
                                                img_cnt=img_len,
                                                register=Account.objects.get(srvno='ADMIN'),
                                                region='정보 없음',
                                                main_img=ContentFile(img_bytes, str(datetime.today())+img_name+'.jpg'))

                ship.save()
                if img_len > 1:
                    for i in range(img_len):
                        if i == 0:
                            continue
                        else:
                            img = Image.open('D:/기존 사용 DB/media/' + img_path[i])
                            img_name = str(uuid.uuid4())
                            buf = BytesIO()
                            img.save(buf, 'jpeg')
                            buf.seek(0)
                            img_bytes = buf.read()
                            buf.close()
                            ship_img = WasteImage.objects.create(w_id=WasteShip.objects.get(id=ship.id),
                                                                 img=ContentFile(img_bytes,
                                                                                 str(datetime.today())+img_name+'.jpg'))
                            ship_img.save()
                            print('{0} / {1}'.format(i, img_len))
                print('{} 선박 등록 완료'.format(ship_id))
            else:
                ship = WasteShip.objects.create(lat=lat,
                                                lon=lon,
                                                info=info,
                                                img_cnt=img_len,
                                                region='정보 없음',
                                                register=Account.objects.get(srvno='ADMIN'),)
                ship.save()
                print('이미지가 없어요 ㅜㅜ')
                print('{} 선박 등록 완료'.format(ship_id))
        return self.success(message='success')


class AllDelete(APIView):
    def get(self, request):
        # img_name = str(uuid.uuid4())
        # image = base64.b64decode(request.data['image_data'][0])
        # image = ContentFile(image, str(datetime.today()) + img_name + '.jpg')
        # ship.main_img = image
        # ship.save()
        return self.success(message='success')
