from utils.custom_view import APIView
from Boats.models import Boat, WasteBoat
from Boats.serializers import BoatSerializer, WasteBoatSerializer
import base64
from django.core.files.base import ContentFile

# from utils.test_crawling import parse_data
# from django.core.files import File
# from io import BytesIO
# import requests
# import random


class DetailBoatAPI(APIView):
    def post(self, request):
        data = Boat.objects.get(id=request.data['id'])
        serializer = BoatSerializer(data)
        return self.success(serializer.data, message='success')


class RegistBoatAPI(APIView):
    def post(self, request):
        if request.data['flag'] == 'Normal':
            serializer = BoatSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return self.fail(message="Request Body Error.")
            image_data = base64.b64decode(request.data['image_data'])
            imo = serializer.validated_data['imo']
            serializer.validated_data['main_img'] = ContentFile(image_data,
                                                                imo+'.jpg')
            serializer.save()
            return self.success(message='success')
        else:
            serializer = WasteBoatSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return self.fail(message="Request Body Error")
            image_data = base64.b64decode(request.data['image_data'])
            title = serializer.validated_data['title']
            serializer.validated_data['wasted_img'] = ContentFile(image_data,
                                                                  title+'.jpg')
            serializer.save()
            return self.success(message='success')


class SearchingBoatAPI(APIView):
    def post(self, request):
        data = Boat.objects.all()
        for key, value in request.data.items():
            if value != '':
                if key == 'name':
                    data = data.filter(name__contains=value)
                elif key == 'imo':
                    data = data.filter(imo__contains=value)
                elif key == 'calsign':
                    data = data.filter(calsign__contains=value)
                elif key == 'mmsi':
                    data = data.filter(mmsi__contains=value)
                elif key == 'vessel_type':
                    data = data.filter(vessel_type__contains=value)
                elif key == 'build_year':
                    data = data.filter(build_year__contains=value)
                elif key == 'current_flag':
                    data = data.filter(current_flag__contains=value)
                elif key == 'home_port':
                    data = data.filter(home_port__contains=value)
        searching_data = BoatSerializer(data, many=True)
        if not len(searching_data.data):
            return self.fail(message='DoesNotExist')
        return self.success(data=searching_data.data, message='success')


class WasteBoatAPI(APIView):
    def post(self, request):
        data = WasteBoat.objects.all()
        serializer = WasteBoatSerializer(data, many=True)
        return self.success(data=serializer.data, message='success')


class WasteDetailBoatAPI(APIView):
    def post(self, request):
        pk = request.data['id']
        data = WasteBoat.objects.get(id=pk)
        serializer = WasteBoatSerializer(data)
        return self.success(data=serializer.data, message='success')


class test(APIView):
    def post(self, request):
        # data_set = []
        # for code in data_set:
        #     code = str(code)
        #     data = parse_data(code)
        #     if data[0] == "":
        #         try:
        #             WasteBoat.objects.get(title=data[1])
        #         except WasteBoat.DoesNotExist:
        #             response = requests.get(data[8])
        #             binary_data = response.content
        #             temp_file = BytesIO()
        #             temp_file.write(binary_data)
        #             lat = 36 + round(random.random(), 6)
        #             lon = 127 + round(random.random(), 6)
        #             boat = WasteBoat.objects.create(latitude=lat,
        #                                             longitude=lon,
        #                                             title=data[1])
        #             boat.wasted_img.save(code+'.jpg', File(temp_file))
        #             print(code + "가 등록됐어요(Wasted)")
        #         except Boat.MultipleObjectsReturned:
        #             print(code + " 가 중복됐어요(Wasted)")
        #     else:
        #         try:
        #             Boat.objects.get(imo=data[1])
        #         except Boat.DoesNotExist:
        #             response = requests.get(data[8])
        #             binary_data = response.content
        #             temp_file = BytesIO()
        #             temp_file.write(binary_data)
        #             boat = Boat.objects.create(name=data[0],
        #                                        imo=data[1],
        #                                        calsign=data[2],
        #                                        mmsi=data[3],
        #                                        vessel_type=data[4],
        #                                        build_year=data[5],
        #                                        current_flag=data[6],
        #                                        home_port=data[7])
        #             boat.main_img.save(code+'.jpg', File(temp_file))
        #             print(code + '가 등록됐어요')
        #         except Boat.MultipleObjectsReturned:
        #             print(code + " 가 중복됐어요")
        # print(WasteBoat.objects.all())
        # for k in range(21,27):
        #     i = WasteBoat.objects.get(id=k)
        #     i.delete()
        # print(WasteBoat.objects.all())
        return self.success(message='success')