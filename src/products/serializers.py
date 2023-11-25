from rest_framework import serializers
from products.models import Product, Tag


class ProductTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["title"]


class ProductSerializer(serializers.ModelSerializer):
    tags = ProductTagSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"



class PostCreateSerializer(serializers.ModelSerializer):
    tags = ProductTagSerializer(many=True, required=False)
    image = serializers.CharField()

    class Meta:
        model = Product
        fields = [
            "image",
            "caption",
            "tags"
        ]

    def create(self, validated_data):
        if validated_data.get("tags") is not None:
            tags = validated_data.pop("tags")
            if len(tags) > 0:
                tag_title_list = []
                for tag in tags:
                    tag_title_list.append(tag["title"].lower())
                existing_tags = Tag.objects.filter(title__in=tag_title_list)
                existing_tag_title_list = []
                for existing_tag in existing_tags:
                    existing_tag_title_list.append(existing_tag.title)
                new_tag_object_list = []
                for tag_title in tag_title_list:
                    if tag_title not in existing_tag_title_list:
                        new_tag_object_list.append(
                            Tag(title=tag_title)
                        )
                if len(new_tag_object_list) > 0:
                    new_tags = Tag.objects.bulk_create(new_tag_object_list)

                # tags_to_be_added = chain(new_tags, existing_tags)
                tags_to_be_added = new_tags + list(existing_tags)

        # validated_data["image"] = os.path.join(settings.MEDIA_ROOT, validated_data["image"])

        request = self.context.get('request')
        user = request.user

        validated_data["user"] = user

        post = super().create(validated_data)
        if validated_data.get("tags") is not None:
            post.tags.add(*tags_to_be_added)
        return post


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["image"]