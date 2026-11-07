from django.db import models

# Create your models here.

class Platform(models.Model):
    igdb_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    abbreviation = models.CharField(max_length=50, null=True, blank=True)
    generation = models.IntegerField(null=True, blank=True)
    platform_family_id = models.BigIntegerField(null=True, blank=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        db_table = "platforms"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Game(models.Model):
    igdb_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    platforms = models.ManyToManyField(
        Platform,
        through="GamePlatform",
        related_name="games"
    )
    raw_data = models.JSONField(default=dict)

    class Meta:
        db_table = "games"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cover(models.Model):
    igdb_id = models.BigIntegerField(primary_key=True)
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="covers"
    )
    image_id = models.CharField(max_length=100)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        db_table = "covers"

    @property
    def image_url(self):
        return (
            f"https://images.igdb.com/igdb/image/upload/"
            f"t_cover_big/{self.image_id}.jpg"
        )

    def __str__(self):
        return self.image_id

# Join table for Game and Platform
class GamePlatform(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="game_platforms"
    )
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name="platform_games"
    )

    class Meta:
        db_table = "game_platforms"
        constraints = [
            models.UniqueConstraint(
                fields=["game", "platform"],
                name="unique_game_platform"
            )
        ]

    def __str__(self):
        return f"{self.game} - {self.platform}"


class TitleCleanupTerm(models.Model):
    CATEGORY_CHOICES = [
        ("unwanted", "Unwanted word"),
        ("seller", "Seller description"),
    ]

    term = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.term


