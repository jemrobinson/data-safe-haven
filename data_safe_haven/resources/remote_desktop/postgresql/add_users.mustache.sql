-- Create users in guacamole_entity table
{{#users}}
INSERT INTO
    guacamole_entity (name, type)
VALUES
    ('{{username}}', 'USER')
ON CONFLICT DO NOTHING;
{{/users}}

-- Create entries in guacamole_user table
-- Note that these passwords should not be used to log-in so we set them to random 64 character strings
{{#users}}
INSERT INTO
    guacamole_user (
        entity_id,
        full_name,
        email_address,
        password_hash,
        password_salt,
        password_date
    )
SELECT
    entity_id,
    '{{full_name}}',
    '{{email_address}}',
    decode(
        '{{password_hash}}',
        'hex'
    ),
    decode(
        '{{password_salt}}',
        'hex'
    ),
    '{{password_date}}'
FROM
    guacamole_entity
WHERE
    guacamole_entity.name = '{{username}}'
    AND guacamole_entity.type = 'USER'
ON CONFLICT DO NOTHING;
{{/users}}

-- Ensure that all users are added to the correct group
TRUNCATE guacamole_user_group_member;
INSERT INTO
    guacamole_user_group_member (
        user_group_id,
        member_entity_id
    )
SELECT
    guacamole_user_group.user_group_id,
    guac_user.entity_id AS member_entity_id
FROM
    guacamole_user_group
    JOIN guacamole_entity guac_group ON guac_group.entity_id = guacamole_user_group.entity_id
    CROSS JOIN guacamole_entity guac_user
WHERE
    guac_user.type = 'USER'
    AND guac_group.name = '{{group_name}}'
ON CONFLICT DO NOTHING;