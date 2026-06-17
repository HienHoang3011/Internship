from rest_framework import serializers
from app.core.models import Test, TestQuestion, QuestionOption, TestResult

class QuestionOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'score']

class TestQuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    options = QuestionOptionSerializer(many=True)

    class Meta:
        model = TestQuestion
        fields = ['id', 'question_text', 'order_number', 'dimension', 'options']

class TestSerializer(serializers.ModelSerializer):
    questions = TestQuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'type', 'description', 'image_url', 'created_at', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        test = Test.objects.create(**validated_data)
        for q_data in questions_data:
            options_data = q_data.pop('options', [])
            question = TestQuestion.objects.create(test=test, **q_data)
            for opt_data in options_data:
                QuestionOption.objects.create(question=question, **opt_data)
        return test

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.description = validated_data.get('description', instance.description)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.save()

        questions_data = validated_data.get('questions', [])
        # Very simple update strategy: delete all old questions and recreate
        # Not the most efficient but works well for this use case
        instance.questions.all().delete()
        for q_data in questions_data:
            q_data.pop('id', None) # remove id if exists
            options_data = q_data.pop('options', [])
            question = TestQuestion.objects.create(test=instance, **q_data)
            for opt_data in options_data:
                opt_data.pop('id', None)
                QuestionOption.objects.create(question=question, **opt_data)
        
        return instance

class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['id', 'user', 'test', 'answers', 'raw_result', 'created_at']
        read_only_fields = ['user', 'created_at']
