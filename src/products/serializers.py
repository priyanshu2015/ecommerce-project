from rest_framework import serializers
from products.models import Product, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["title"]
        extra_kwargs = {
            "title": {
                "validators": []
            }
        }


class CreateProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    image = serializers.CharField(required=False)
    
    class Meta:
        model = Product
        fields = [
            "image",
            "name",
            "tags",
            "price"
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
                new_tags = []
                if len(new_tag_object_list) > 0:
                    new_tags = Tag.objects.bulk_create(new_tag_object_list)
                
                tags_to_be_added = new_tags + list(existing_tags)

        request = self.context.get('request')
        user = request.user
        validated_data["admin_user"] = user
        product = super().create(validated_data)
        if len(tags) > 0:
            product.tags.add(*tags_to_be_added)
        return product


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"