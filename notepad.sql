SELECT 
    g.group_id, 
    g.group_name, 
    g.group_description, 
    g.group_id, ug.user_id, 
    ug.group_creator, 
    u.username
FROM groups g JOIN users_groups ug ON g.group_id = ug.group_id
    JOIN users u ON u.user_id = ug.user_id
WHERE ug.user_id IN (SELECT ug.user_id FROM users_groups ug WHERE ug.group_id = ?)